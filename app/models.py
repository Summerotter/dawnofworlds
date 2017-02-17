from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from flask import current_app, request
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager
from random import randint


class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    WRITE_ARTICLES = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.WRITE_ARTICLES, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.WRITE_ARTICLES |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name


player_world_table = db.Table('player_worlds', db.Model.metadata,
                               db.Column('player_id', db.Integer,
                                         db.ForeignKey('users.id')),
                               db.Column('world_id', db.Integer,
                                         db.ForeignKey('world.id')))
    

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    avatar_hash = db.Column(db.String(32))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    armies = db.relationship('Armies', backref='army_owner', lazy='dynamic')
    turnlog = db.relationship('TurnLog', backref='player_turn', lazy='dynamic')
    events = db.relationship('Events', backref='player_event', lazy='dynamic')
    races = db.relationship('Race', backref='race_creator', lazy='dynamic')
    avatars = db.relationship('Avatars', backref='avatar_owner', lazy='dynamic')
    orders = db.relationship('Orders', backref='order_owner', lazy='dynamic')
    owned_worlds = db.relationship('World', backref='world_owner', lazy='dynamic')
    worlds = db.relationship('World',
                             secondary=player_world_table,
                             backref =db.backref('players', lazy='dynamic'),
                             lazy='dynamic')
    points = db.relationship('PowerPoints', backref='player_points',lazy='dynamic')


    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(
                self.email.encode('utf-8')).hexdigest()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
            (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

    def __repr__(self):
        return '<User %r>' % self.username
        
    def get_id(self):
        return self.id
        
    def return_points_obj(self,world_id):
        points = self.points.filter_by(world=world_id).first()
        try:
            points.points >= 0
        except:
            points = PowerPoints()
            points.points = 0
        return points
        
    def is_anon(self):
        return False


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False
        
    def return_points_obj(self,world_id):
        points = PowerPoints()
        points.points = -1
        return points
        
    def is_anon(self):
        return True

login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
   return User.query.get(user_id)


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py

        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                     timestamp=forgery_py.date.date(True),
                     author=u)
            db.session.add(p)
            db.session.commit()

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(
            markdown(value, output_format='html'),
            tags=allowed_tags, strip=True))

db.event.listen(Post.body, 'set', Post.on_changed_body)
from app import db
from hashlib import md5
from flask import url_for


                                         
order_location_table = db.Table('order_location', db.Model.metadata,
                               db.Column('order_id', db.Integer,
                                         db.ForeignKey('orders.id')),
                               db.Column('location_id', db.Integer,
                                         db.ForeignKey('worldmap.id')))
                                         
                                                               
class OrderTypes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    text = db.Column(db.String(64))
    def insert_orders():
        orders = ('Cultural Religion', 'Religious', "Military","Trade","Criminal","Technology","Magic")
        for o in orders:
            order = OrderTypes.query.filter_by(text=o).first()
            if order is None:
                order = OrderTypes(text=o)
            db.session.add(order)
        db.session.commit()


class WorldMap(db.Model):
    __tablename__ = 'worldmap'
    id = db.Column(db.Integer, primary_key=True)
    world = db.Column(db.Integer, db.ForeignKey('world.id'))
    race = db.Column(db.Integer,db.ForeignKey('race.id'),default=0)
    race_color = db.Column(db.Integer,default=0)
    letter_coord = db.Column(db.Integer)
    number_coord = db.Column(db.Integer)
    terrain = db.Column(db.String(16))
    image = db.Column(db.String(16))
    city = db.relationship("City",backref='world_location',lazy='dynamic')
    has_city = db.Column(db.Integer)
    army = db.relationship("Armies",backref='worldmap_id',lazy='dynamic')
    events = db.relationship("Events",backref="worldmap_event_id",lazy='dynamic')
    prov_bldg = db.relationship("BldgProv",backref="worldmap",lazy='dynamic')
    avatars = db.relationship("Avatars",backref="worldmap_avatar",lazy='dynamic')
    
    
    def coords(self):
        return str(self.letter_coord)+"x/"+str(self.number_coord)+"y"
        
    def regen_coords(self):
        return {"y":self.number_coord,"x":int(self.letter_coord),}
        
    def return_image(self):
        return url_for('static',filename="image/"+self.image)
        
    def return_race(self):
        return Race.query.get(self.race)
        
    def return_live_city(self):
        return self.city.filter_by(is_alive=1).first()
        
    def return_live_provbldge(self):
        return self.prov_bldg.filter_by(is_alive=1).all()
        
    def return_ruin_city(self):
        return self.city.filter_by(is_alive=0).all()
        
    def return_ruin_provbldg(self):
        return self.prov_bldg.filter_by(is_alive=0).all()
        


class World(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64),index=True,unique=True)
    age = db.Column(db.Integer ,index=True, default=1)
    turn_of_age = db.Column(db.Integer, index=True,default=1)
    total_turns = db.Column(db.Integer, index=True,default=1)
    races = db.relationship('Race', backref='homeworld', lazy='dynamic')
    active = db.Column(db.Integer,default=0)
    cities = db.relationship('City', backref='city_homeworld', lazy='dynamic')
    avatars = db.relationship("Avatars", backref='avatar_homeworld', lazy='dynamic')
    turnlog = db.relationship("TurnLog", backref='turnlog_homeworld', lazy='dynamic')
    event = db.relationship("Events", backref='event_homeworld', lazy='dynamic')
    orders = db.relationship("Orders", backref='order_homeworld', lazy='dynamic')
    provbldg = db.relationship("BldgProv", backref="world",lazy='dynamic')
    armies = db.relationship("Armies", backref="worldid",lazy='dynamic')
    history = db.relationship("WorldHistory",backref="worldbackref",lazy='dynamic')
    points = db.relationship('PowerPoints', backref='world_points',lazy='dynamic')
    size = db.Column(db.Integer,default=50)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))
                                                         
    def __repr__(self):
        return '<World %r>' % (self.name)

    def age_turn(self):
        return "A"+str(self.age)+":T"+str(self.turn_of_age)
        
    def ret_history(self):
        return WorldHistory.query.filter_by(world=self.id).order_by(WorldHistory.id.desc())
        
    def delete_self(self):
        for each in self.provbldg.all():
            db.session.delete(each)
        for each in self.armies.all():
            db.session.delete(each)
        for each in self.history.all():
            db.session.delete(each)
        for each in self.points.all():
            db.session.delete(each)
        for each in self.avatars.all():
            db.session.delete(each)
        for each in self.event.all():
            db.session.delete(each)
        for each in self.orders.all():
            for location in each.locations.all():
                db.session.delete(location)
            db.session.delete(each)
        for each in Race.query.filter_by(world_id=self.id).all():
            each.remove_stuff()
            db.session.delete(each)
        for each in self.cities:
            each.remove_stuff()
            db.session.delete(each)
        for each in WorldMap.query.filter_by(world=self.id).all():
            db.session.delete(each)
        db.session.commit()
            

class Race(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'))
    #Check culture_name when calling to make certain unique per world
    culture_name = db.Column(db.String(128),index=True)
    race_name = db.Column(db.String(64))
    map_color = db.Column(db.Integer)
    alignment = db.Column(db.Integer)
    creator = db.Column(db.Integer, db.ForeignKey('users.id'))
    abs_turn_made = db.Column(db.Integer)
    age_turn = db.Column(db.String(64))
    #subrace - 0 or race_id
    subrace = db.Column(db.Integer, default=0)
    controlled_cities = db.relationship('City', backref='city_builders', lazy='dynamic')
    controlled_provbldg = db.relationship('BldgProv', backref='bldgprov_builders', lazy='dynamic')
    armies = db.relationship('Armies', backref='culture', lazy='dynamic')
    orders = db.relationship("Orders", backref='founders',lazy='dynamic')
    religion = db.Column(db.Integer)
    location = db.relationship("WorldMap",backref='race_location',lazy='dynamic')
    advances = db.relationship("RaceAdvances",backref="race_obj",lazy='dynamic')
    
    def remove_stuff(self):
        #part of deleting a world
        for each in self.advances.all():
            db.session.delete(each)
        for each in self.location.all():
            db.session.delete(each)
        for each in self.armies.all():
            db.session.delete(each)
        db.session.commit()
    
    
    def subrace_of(self):
        if self.subrace == 0:
            return "None"
        else:
            parent_id = self.subrace
            parent = Race.query.get(parent_id)
            return parent.culture_name

    def made_by(self):
        if self.creator == 0 or self.creator == None:
            return "Orphaned"
        else:
            creator = User.query.get(self.creator)
            return creator.name
            
    def get_religion(self):
        if self.religion == 0:
            return None
        elif self.religion == None:
            return None
        else:
            religion = Orders.query.get(self.religion)
            return religion
    
class City(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'))
    name = db.Column(db.String(64))
    #Building Race's ID
    built_by = db.Column(db.Integer)
    owned_by = db.Column(db.Integer, db.ForeignKey('race.id'))
    location = db.Column(db.Integer, db.ForeignKey('worldmap.id'))
    alignment = db.Column(db.Integer)
    buildings = db.relationship("BldgCity", backref="bldg_here", lazy='dynamic')
    armies = db.relationship("Armies", backref='army_built_here', lazy='dynamic')
    age_turn = db.Column(db.String(64))
    turn_built = db.Column(db.Integer)
    is_alive = db.Column(db.Integer, default = 1)
    destroyed_in = db.Column(db.Integer)
    history = db.relationship("CityHistory",backref="history",lazy='dynamic')
    orders = db.relationship("Order_City",backref="order_city_cityobj",lazy='dynamic')
    advances = db.relationship("CityAdvances",backref="city_obj",lazy='dynamic')
    
    def remove_stuff(self):
        for each in self.buildings.all():
            db.session.delete(each)
        for each in self.history.all():
            db.session.delete(each)
        for each in self.advances.all():
            db.session.delete(each)

    def builder_name(self):
        builder = Race.query.get(self.built_by)
        return builder.culture_name

    def owner_name(self):
        if self.is_alive:
            owner = Race.query.get(self.owned_by)
            return owner.culture_name
        else:
            return "Ruins"
    
    def ret_history(self):
        return CityHistory.query.filter_by(cityid=self.id).order_by(CityHistory.id.desc())
        
    def return_location(self):
        return WorldMap.query.get(self.location)
        
    def return_owner_player(self):
        race = Race.query.get(self.owned_by)
        player = User.query.get(race.creator)
        return player.id

class BldgCity(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    desc = db.Column(db.String(64))
    built_in = db.Column(db.Integer, db.ForeignKey('city.id'))
    age_turn = db.Column(db.String(64))
    turn_built = db.Column(db.Integer)

class BldgProv(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    #Building race's ID
    built_by = db.Column(db.Integer)
    world_in = db.Column(db.Integer, db.ForeignKey('world.id'))
    owned_by = db.Column(db.Integer, db.ForeignKey('race.id'))
    location = db.Column(db.Integer, db.ForeignKey('worldmap.id'))
    name = db.Column(db.String(64))
    description = db.Column(db.String(64))
    age_turn = db.Column(db.String(64))
    turn_built = db.Column(db.Integer)
    is_alive = db.Column(db.Integer)
    destroyed_in = db.Column(db.String())

    def builder_name(self):
        builder = Race.query.get(self.built_by)
        return builder.culture_name

    def owner_name(self):
        if self.is_alive:
            owner = Race.query.get(self.owned_by)
            return owner.culture_name
        else:
            return "Ruins"
            
    def owner_id(self):
        if self.is_alive:
            owner = Race.query.get(self.owned_by)
            return owner.creator
        else:
            return 0

    def new_owner(self, owner):
        if self.owned_by != owner:
            self.owned_by = owner
            
    def return_location(self):
        return WorldMap.query.get(self.location)
        
class Order_City(db.Model):
    __tablename__ = 'order_city'
    id = db.Column(db.Integer,primary_key=True)
    order_id = db.Column(db.Integer,db.ForeignKey('orders.id'))
    city_id = db.Column(db.Integer,db.ForeignKey('city.id'))
    
    def return_city(self):
        return City.query.get(self.city_id)
        
    def return_order(self):
        return Orders.query.get(self.order_id)

class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))
    world = db.Column(db.Integer, db.ForeignKey('world.id'))
    description = db.Column(db.String(128))
    name = db.Column(db.String(64))
    abs_turn = db.Column(db.Integer)
    age_turn = db.Column(db.String(128))
    is_alive = db.Column(db.Integer)
    type = db.Column(db.Integer)
    #1=cultural_religion_DONOTDELETE,2=religion, 3=military, 4=trade, 5=criminal,6=research, 7=magical
    founding_culture = db.Column(db.Integer, db.ForeignKey('race.id'))
    cities = db.relationship("Order_City",backref="order_city_orderobj",lazy='dynamic')
    locations = db.relationship('WorldMap',
                             secondary=order_location_table,
                             backref =db.backref('orders', lazy='dynamic'),
                             lazy='dynamic')
    
    def owner_name(self):
        owner = User.query.get(self.owner)
        return owner.name
        
        
    def order_type(self):
        if self.type:
            type = OrderTypes.query.get(self.type)
            if type == None:
                return "None"
            else:
                return type.text
        else:
            return "None"
            

class Events(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    age_turn = db.Column(db.String(64))
    abs_turn = db.Column(db.Integer)
    location = db.Column(db.Integer,db.ForeignKey('worldmap.id'))
    event_info = db.Column(db.String(128))
    played_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    world = db.Column(db.Integer, db.ForeignKey('world.id'))
    duration = db.Column(db.Integer)

    def playedby_name(self):
        return User.query.get(self.played_by).name
        
    def return_location(self):
        return WorldMap.query.get(self.location)
        
class Unit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(24))
    power = db.Column(db.Float)
    health = db.Column(db.Integer)
    max_health = db.Column(db.Integer)
    assigned_army = db.Column(db.Integer, db.ForeignKey('armies.id'))
    player = db.Column(db.Integer, db.ForeignKey("users.id"))
    world = db.Column(db.Integer, db.ForeignKey("world.id"))
    
    def attack(self):
        return random.randint(1,10)*(self.power*(self.health/self.max_health))
        
class Armies(db.Model):
    #and also navies!
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    #1 for armies, 0 for navies
    army = db.Column(db.Integer)
    supported_from = db.Column(db.Integer, db.ForeignKey('city.id'))
    home_culture = db.Column(db.Integer, db.ForeignKey('race.id'))
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))
    location = db.Column(db.Integer,db.ForeignKey('worldmap.id'))
    world = db.Column(db.Integer,db.ForeignKey('world.id'))
    home_city = db.Column(db.Integer)
    is_alive = db.Column(db.Integer, default=1)
    movement_range = db.Column(db.Integer, default=2)
    has_moved = db.Column(db.Integer, default=0)

    def army_navy(self):
        if self.army:
            return "Army"
        else:
            return "Navy"

    def owner_name(self):
        return User.query.get(self.owner).name

    def homecity_name(self):
        return City.query.get(self.home_city).name

    def homeculture_name(self):
        return Race.query.get(self.home_culture).culture_name
        
    def supporting_city(self):
        if self.supported_from:
            return City.query.get(self.supported_from).name
        else:
            return "Orphaned"
            
    def return_location(self):
        return WorldMap.query.get(self.location)
        
    def attack(self):
        attack_total = 0
        units = Unit.query.filter_by(assigned_army=self.id).all()
        if units:
            for unit in units:
                attack_total += unit.attack()
        return attack_total
        
    def unit_count(self):
        units = Unit.query.filter_by(assigned_army=self.id).all()
        return len(units)

class TurnLog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    world_id = db.Column(db.Integer, db.ForeignKey('world.id'))
    age_turn = db.Column(db.String(64))
    abs_turn = db.Column(db.Integer)
    player = db.Column(db.Integer, db.ForeignKey('users.id'))
    actions = db.Column(db.String(256))

class Avatars(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'))
    world = db.Column(db.Integer, db.ForeignKey('world.id'))
    #birthed_race = 0 or Race.Primary.Key
    birthed_race = db.Column(db.Integer, default=0)
    description = db.Column(db.String(64))
    abs_turn = db.Column(db.Integer)
    age_turn = db.Column(db.String(64))
    location = db.Column(db.Integer, db.ForeignKey('worldmap.id'))
    name = db.Column(db.String(64))
    is_alive = db.Column(db.Integer,default=1)
    movement_range = db.Column(db.Integer,default=3)
    has_moved = db.Column(db.Integer,default=0)

    def owner_name(self):
        return User.query.get(self.owner).name
        
        
    def return_location(self):
        return WorldMap.query.get(self.location)

class CityHistory(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    cityid = db.Column(db.Integer, db.ForeignKey('city.id'))
    abs_turn = db.Column(db.Integer)
    age_turn = db.Column(db.String(64))
    entry = db.Column(db.String(256))

class WorldHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    world = db.Column(db.Integer, db.ForeignKey('world.id'))
    abs_turn = db.Column(db.Integer)
    age_turn = db.Column(db.String(64))
    text = db.Column(db.String(256))
    
    def worldname(self):
        return World.query.get(self.world).name
        

class PowerPoints(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.Integer,db.ForeignKey('users.id'))
    world = db.Column(db.Integer,db.ForeignKey('world.id'))
    points = db.Column(db.Integer,default=0)
    bonus = db.Column(db.Integer,default=0)
    is_ready = db.Column(db.Integer,default=0)
    player_status = db.Column(db.String,default="pending")
    
class CityAdvances(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    text = db.Column(db.String(256))
    
class RaceAdvances(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    race_id = db.Column(db.Integer, db.ForeignKey('race.id'))
    text = db.Column(db.String(256))
    
#library items start here

class Books(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(256))
    primary_author = db.Column(db.Integer, db.ForeignKey('author.id'))
    publisher = db.Column(db.Integer, db.ForeignKey('publisher.id'))
    series = db.Column(db.Integer, db.ForeignKey('series.id'))
    series_number = db.Column(db.Integer)
    published = db.Column(db.Integer)
    small_blurb = db.Column(db.Text)
    large_review = db.Column(db.Text)
    
    
    
class Author(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256))
    books = db.relationship("Books",backref="author_obj",lazy='dynamic')
    
class Publisher(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256))
    books = db.relationship("Books",backref="publisher_obj",lazy='dynamic')
    
class Series(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(256))
    books = db.relationship("Books",backref="series_obj",lazy='dynamic')