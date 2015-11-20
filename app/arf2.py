class Player(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(64))
    #armies, turnlog, events, races, avatars, orders
    armies = db.relationship('Armies', backref='army_owner', lazy='dynamic')
    turnlog = db.relationship('TurnLog', backref='player_turn', lazy='dynamic')
    events = db.relationship('Events', backref='player_event', lazy='dynamic')
    races = db.relationship('Race', backref='race_creator', lazy='dynamic')
    avatars = db.relationship('Avatars', backref='avatar_owner', lazy='dynamic')
    orders = db.relationship('Orders', backref='order_owner', lazy='dynamic')
    worlds = db.relationship('World',
                             secondary=player_world_table,
                             backref =db.backref('players', lazy='dynamic'),
                             lazy='dynamic')
    points = db.relationship('PowerPoints', backref='player_points',lazy='dynamic')
    

    def is_authenticated():
        True

    def is_active():
        True

    def is_anonymous():
        True

    def get_id(self):
        return str(id)
    
    def return_points_obj(self,world_id):
        points = self.points.filter_by(world=world_id).first()
        return points