from flask import render_template, flash, redirect, session, url_for, request, g, make_response, abort, current_app
from flask.ext.login import login_required, current_user

from . import game, points_table
from .. import db
from .forms import *
from ..models import *
from config import *
from random import randint
from noise import snoise2
from ..decorators import admin_required, permission_required
point_costs = points_table.points_table

#temp workaround
POSTS_PER_PAGE = 15
world_active = None

@game.route("/randomchar",methods=['GET','POST'])
def character_builder():
    species = ['Fox', 'Wolf', 'Cat', 'Leopard', 'Cheetah', 'Lion', 'Otter', 'Badger', 'Skunk', 'Rabbit', 'Gerbil', 'Hamster', 'Tiger', 'Lynx', 'Honey Badger', 'Dingo', 'Shiba-Inu', 'Malamute', 'Hare', 'Liger', 'Snow Leopard', 'Serval', 'Cow/Bull', 'Rat', 'German Shepard', 'Bulldog', 'Border Collie', 'Squirrel', 'Mouse', 'Sugar Glider', 'Possum', 'Ram', 'Dalmatian', 'Goat', 'Stallion', 'Horse', 'Sheep', 'Pig', 'Mouse', 'GuineaPig', 'Elephant', 'Gazelle', 'Gazebo', 'Boar', 'Deer', 'Caribou', 'Terrier', 'Boxer', 'Corgi', 'Golden Retriever', 'Reindeer', 'Great Dane', 'Mastiff', 'Old English Sheepdog', 'Pug', 'Donkey', 'Cougar', 'Bat', 'Eastern Dragon', 'Western Dragon', 'Giraffe', 'Rhino', 'Ferret', 'Mink', 'Pine Marten', 'Crow', 'Pelican', 'Hawk', 'Griffin', 'Crocodile', 'Alligator', 'Snake', 'Serpentine Dragon', 'Wyvern', 'Blue Tit', 'Hippo', 'Zebra', 'Seal', 'Seal-lion', 'Walrus', 'Bear', 'Panda', 'Red Panda', 'Polar Bear', 'Samoyed', 'Miniature Pinscher', 'Antelope', 'Anteater', 'Coyote', 'Jackal', 'Hedgehog', 'Hyena', 'Meerkat', 'Koala', 'Furred Eastern Dragon', 'Furred Western Dragon', 'Mongoose', 'Raccoon', 'Beaver', 'Monkey', 'Ape', 'Gorilla', 'Lemur', 'Weasel', 'Wolverine', 'Unicorn', 'Phoenix', 'Owl', 'Dolphin', 'Shark', 'Whale', 'Crux', 'Qwhilla', 'Sergal', 'Tanuki', 'Naga', 'Dinosaur', 'T-Rex', 'Raptor', 'Turtle', 'Lizard','Minotaur',]
    gender = ["male", "female","herm","ungendered"]
    height = ["very short", "short", "average height", "tall", "very tall"]
    weight = ["very thin", "thin", "average weight", "husky", "fluffy", "fat", "very fat"]
    build = ["thin", "out of shape", "swimmers", "fit", "body-builder"]
    eye_color = ["blue","green","brown",'gold','yellow','purple','red','orange']
    fur_color = ["red", "brown", "golden", "white", "grey", "black", "orange"]
    accessory = ["a scar", "an eyepatch", "a jaunty hat", "gloves", "Monocle", "Scarf", "Glasses", "Sunglasses"]
    personality = ["Cocky", "Shy", "Naive", "Aggressive", "Calm", "oblivious"]
    job = ["cook", "mechanic", "programmer", "pilot", "mercenary"]
    food = ["rice", "pizza", "steak", "salad", "soup", "noodles"]
    fear = ["spiders", "heights", "water", "insects", "volcanoes", "My Little Pony", "mormons", "the dark", "Lizards"]
    extras = ["Tauric", "Demonic", "Quadrupedal", "Angelic", "Satyric"]
    sex_pref = ["bisexual", "homosexual", "heterosexual", "asexual",]
    chosen_species = species[(randint(1,len(species))-1)]
    chosen_height = height[(randint(1,len(height))-1)]
    chosen_weight = weight[(randint(1,len(weight))-1)]
    chosen_build = build[(randint(1,len(build))-1)]
    chosen_eye_color = eye_color[(randint(1,len(eye_color))-1)]
    chosen_fur_color = fur_color[(randint(1,len(fur_color))-1)]
    chosen_accessory = accessory[(randint(1,len(accessory))-1)]
    chosen_personality = personality[(randint(1,len(personality))-1)]
    chosen_job = job[(randint(1,len(job))-1)]
    chosen_food = food[(randint(1,len(food))-1)]
    chosen_fear = fear[(randint(1,len(fear))-1)]
    chosen_sex_pref = sex_pref[(randint(1,len(sex_pref))-1)]
    if randint(1,100) <= 40:
        chosen_extras = extras[(randint(1,len(extras))-1)]
    else:
        chosen_extras = "Anthro"
    chosen_gender = gender[(randint(1,len(gender))-1)]
    if chosen_gender == 'male':
        pronoun = "He"
    elif chosen_gender == "female":
        pronoun = "She"
    elif chosen_gender == "herm":
        pronoun = "Shi"
    else:
        pronoun = "It"
    return render_template("game/character.html", species=chosen_species, gender=chosen_gender, height=chosen_height, weight=chosen_weight, build=chosen_build, eye_color=chosen_eye_color,
                            fur_color=chosen_fur_color, accessory=chosen_accessory, personality=chosen_personality, job=chosen_job, food=chosen_food, fear=chosen_fear, pronoun=pronoun, sex_pref=chosen_sex_pref)


@game.route('/make-world/',methods=['GET','POST'])
@login_required
@admin_required
def make_world():
    form = MakeWorld()
    if form.validate_on_submit():
        width = form.size.data
        new_world = World(name=form.world.data, age=1, turn_of_age=1, total_turns=1,size=width,)
        db.session.add(new_world)
        db.session.commit()
        world = World.query.order_by(World.id.desc()).first()
        world_gen = {}
        scale = 1/48.0
        coords = range(width)
        base = randint(1,48274)

        for y in coords:
            world_gen[y] = {}
            for x in coords:
                world_gen[y][x] = snoise2(x * scale, y * scale, octaves=4, persistence=0.75,base=base)
        count_letter = 0
        count_number = 0
        for y in world_gen:
            count_number = 0
            for x in world_gen[y]:
                if world_gen[y][x] < -0.10:
                    terrain_result = ['W','water.png']
                elif 0.35 > world_gen[y][x] >= 0.15:
                    terrain_result = ['F', 'forest.png']
                elif 0.55 >= world_gen[y][x] >= 0.35:
                    terrain_result = ['H','hills.png']
                elif world_gen[y][x] > 0.55:
                    terrain_result = ['M','mountains.png']
                else:
                    terrain_result = ['G','grassland.png']
                location = WorldMap(world=world.id, letter_coord=count_letter,number_coord=count_number, terrain=terrain_result[0],image=terrain_result[1])    
                count_number += 1
                db.session.add(location)
            count_letter += 1
        db.session.commit()
        flash("Your world is now made")
        return redirect(url_for('.index'))
    return render_template("/game/make_world.html",form=form, active_world=world_active)
  
@game.route("/",methods=['GET', 'POST'])
@game.route('/index/', methods=['GET', 'POST'])
@login_required
#The home page. Select Worlds Here
def index():
    if 'user' in session:
        user = session['user']
    else:
        user = ''
    if 'active_world' in session:
        world_active = World.query.get(session['active_world'])
    else:
        world_active = ""
    world_list = World.query.all()
    players = User.query.all()
    return render_template("/game/index.html",
                           worlds=world_list,
                           active_world=world_active,
                           players=players,
                           User=User,
                           )

@game.route("/delete/<world_id>",methods=['GET','POST'])
@login_required
@admin_required
def delete_world(world_id):
    world = World.query.get(world_id)
    world.delete_self()
    db.session.delete(world)
    db.session.commit()
    flash("World deleted.")
    return redirect(url_for('.index'))

@game.route("/deleteall",methods=['GET','POST'])
@login_required
@admin_required
def delete_all():
    worlds = World.query.all()
    for each in worlds:
        each.delete_self()
        db.session.delete(each)
    db.session.commit()
    flash("You nuked the universe!")
    return redirect(url_for('.index'))
    
                           
@game.route("/activate/<world_id>", methods=['GET', 'POST'])
@login_required
#Probably could have made this a function of index()
#Swaps between active worlds cause I'm a derp
def activate(world_id):
    session['active_world'] = world_id
    world = World.query.get(world_id)
    flash("World set:"+world.name)
    return redirect(url_for('.index'))
    
@game.route("/world", methods=['GET', 'POST'])
@game.route('/world/<int:page>', methods=['GET', 'POST'])
@login_required
#Expanded basic info ont he world,player list, and add players.
#Needs to have an edit for player names and worldname, here.
def world_page(page=1):
    world = World.query.get(session['active_world'])
    if world is None:
        flash("You need to select a world before accessing this page")
        return redirect(url_for('.index'))
    if request.form:
        if 'points' in request.form:
            points = request.form['points']
            player = request.form['player']
            pointobj = PowerPoints.query.filter_by(world=world.id,player=player).first()
            pointobj.points = points
            db.session.add(pointobj)
            db.session.commit()
            flash("You did some points")
            return redirect(url_for('.world_page'))
    history = world.ret_history().paginate(page, POSTS_PER_PAGE, False)
    newplayer = AddPlayer()
    advanceturn = AdvanceTurn(prefix="turn")
    updatepoints = UpdatePoints()
    advance_age = AdvanceAge(prefix="age")
    history_entry = HistoryEntry()
    players = User.query.filter(~User.worlds.contains(world))
    newplayer.player_list.choices= []
    new_owner = WorldOwner()
    new_owner.player_list.choices= []
    for player in players:
        newplayer.player_list.choices.append([player.id,player.name])
    if world.owner:    
        owner = User.query.get(world.owner)
    else:
        owner = ""
    owner_list = world.players.all()
    players = world.players.all()
    for player in players:
        new_owner.player_list.choices.append([player.id,player.name])
    if new_owner.validate_on_submit():
        world.owner = new_owner.player_list.data
        db.session.add(world)
        db.session.commit()
        flash("New World Owner")
        return redirect(url_for('.world_page'))
    if history_entry.validate_on_submit():
        text = history_entry.text.data
        new_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=text,)
        db.session.add(new_history)
        db.session.commit()
        return redirect(url_for('.world_page'))
    if newplayer.validate_on_submit():
        player = User.query.get(newplayer.player_list.data)
        world.players.append(player)
        pointroll = randint(1,6)+randint(1,6)
        points = PowerPoints(world=world.id,player=player.id,points=pointroll,)
        db.session.add(points)
        db.session.commit()
        flash("You have added "+player.name+" to "+world.name+"!")
        return redirect(url_for('.world_page'))
    if advanceturn.validate_on_submit():
        flash("You have advanced "+world.name+" a turn!")
        world.turn_of_age += 1
        world.total_turns += 1
        db.session.add(world)
        players = world.players
        for player in players:
            pointroll = randint(1,6)+randint(1,6)
            points = player.return_points_obj(world.id)
            if (points.points <= 5) and (points.bonus < 3):
                points.bonus += 1
            elif points.points > 5:
                points.bonus = 0
            points.points = points.points + pointroll + points.bonus
            db.session.add(points)
        events = world.event.all()
        for event in events:
            if event.duration:
                if (event.duration >0) and (event.duration <9001):
                    event.duration -= 1
                    db.session.add(event)
        db.session.commit()
        return redirect(url_for('.world_page'))
    if advance_age.validate_on_submit():
        if world.age < 3:
            flash("You have advanced "+world.name+" to the next age!")
            world.age += 1
            world.turn_of_age=1
            world.total_turns +=1
            db.session.add(world)
            players = world.players
            for player in players:
                pointroll = randint(1,6)+randint(1,6)
                points = player.return_points_obj(world.id)
                if (points.points <= 5) and (points.bonus < 3):
                    points.bonus += 1
                elif points.points > 5:
                    points.bonus = 0
                points.points = points.points + pointroll + points.bonus
                db.session.add(points)
            db.session.commit()
        else:
            flash(world.name+" is already at the Third Age!")
        return redirect(url_for('.world_page'))
    return render_template("/game/world.html",
                           active_world=world,
                           newplayer=newplayer,
                           players=players,
                           advance_turn=advanceturn,
                           advance_age=advance_age,
                           User=User,
                           history=history,
                           updatepoints=updatepoints,
                           history_entry=history_entry,
                           owner=owner,
                           new_owner=new_owner,)

@game.route("/players/<userid>/")
@login_required
def userpage(userid):
    user = User.query.get(userid)
    return redirect(url_for('main.user',username=user.username))

@game.route("/players", methods=["GET","POST"])
@login_required
def player_page():
    players = User.query.all()
    if 'active_world' not in session:
        session['active_world'] = ""
    world = World.query.get(session['active_world'])
    return render_template("/game/players.html",
                           active_world=world,
                           players = players,)

@game.route("/races", methods=['GET','POST'])
@login_required
#Create races here. Need to allow edits for alignment and advances
#Maybe specific /races/<racename> page?
def races_page():
    world = World.query.get(session['active_world'])
    if world is None:
        flash("You need to select a world before accessing this page")
        return redirect(url_for('.index'))
    races = Race.query.filter_by(world_id=world.id).all()
    form = MakeRace()
    players = world.players.all()
    player_list = []
    if current_user.id == world.owner:
        for player in players:
            player_list.append([player.id,player.name])
    else:
        player_list.append([current_user.id,current_user.name])
    form.made_by.choices = player_list
    race_list = [[0,"Not a Subrace"],]
    for race in races:
        race_list.append([race.id,race.culture_name])  
    form.subrace.choices = race_list
    if form.validate_on_submit():
        location = WorldMap.query.filter_by(letter_coord=form.letter.data,number_coord=form.number.data,world=world.id).first()
        race_check = Race.query.filter_by(world_id=world.id,culture_name=form.culture.data).all()
        if race_check:
            flash("Already a culture by that name")
            return redirect(url_for(".races_page"))
        if location.race:
            flash("There is already a race at this location")
            return redirect(url_for(".races_page"))
        if request:
            color = request.form['color']
            if Race.query.filter_by(world_id=world.id).filter_by(map_color=color).all():
                flash("Racial color taken")
                return redirect(url_for(".races_page"))
        points = current_user.return_points_obj(world.id)
        if form.subrace.data == 0:
            if points.points < point_costs[world.age]['Create Subrace']:
                flash("You do not have enough points for this")
                return redirect(url_for(".races_page"))
        else:
            if points.points < point_costs[world.age]['Create Race']:
                flash("You do not have enough points for this")
                return redirect(url_for(".races_page"))
#        if True:
#            flash("Temporary redirect")
#            return redirect(url_for(".races_page"))
        new_race = Race(race_name=form.race.data,
                        culture_name=form.culture.data,
                        map_color = color,
                        alignment = form.align.data,
                        world_id=world.id,
                        abs_turn_made=world.total_turns,
                        subrace = form.subrace.data,
                        age_turn=world.age_turn(),
                        creator = form.made_by.data,
                        religion = 0,)
        religion_description = "The cultural religion of the "+form.culture.data
        db.session.add(new_race)
        points.points -= point_costs[world.age]['Create Race']
        db.session.add(points)
        db.session.commit()
        race = Race.query.order_by(Race.id.desc()).first()
        new_order = Orders(name=form.religion.data,
                           owner=current_user.id,
                           description=religion_description,
                           abs_turn=world.total_turns,
                           age_turn=world.age_turn(),
                           is_alive=1,
                           world=world.id,
                           founding_culture=race.id,
                           type=1,)
        db.session.add(new_order)
        db.session.commit()
        order = Orders.query.order_by(Orders.id.desc()).first()
        race.religion = order.id
        db.session.add(race)
        location.race = race.id
        db.session.add(location)
        order.locations.append(location)
        db.session.add(order)
        hist_text = race.made_by()+" made the "+race.culture_name+" "+race.race_name+" with the "+order.name+" religion."
        new_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(new_history)
        db.session.commit()
        flash("Your new race is now made")
        return redirect(url_for('.races_page'))
    return render_template("/game/races.html",
                           active_world=world,
                           races=races,
                           form=form,
                           user=current_user,
                           race_cost=point_costs[world.age]['Create Race'],
                           subrace_cost=point_costs[world.age]['Create Subrace'],)

@game.route("/races/<race>/",methods=['GET','POST'])
@login_required
def single_race(race):
    race = Race.query.get(race)
    world = World.query.get(session['active_world'])
    if race is None:
        flash("That doesn't exist")
        return redirect(url_for('.world_page'))
    if race.world_id != world.id:
        flash("That doesn't exist in the active world")
        return redirect(url_for('.world_page'))
    cities = race.controlled_cities.filter_by(is_alive=1).all()
    form = UpdateLocation(prefix="location")
    advance_form = HistoryEntry(prefix="advance")
    advance_remove = ArmySupportFrom(prefix="remove_adv")
    advances = race.advances.all()
    advance_list = []
    for advance in advances:
        advance_list.append([advance.id,advance.text])
    advance_remove.support.choices = advance_list
    remove_form = ArmySupportFrom(prefix="remove")
    choices = []
    locations = race.location.all()
    for location in locations:
        choices.append([location.id,location.coords()])
    remove_form.support.choices = choices
    if form.validate_on_submit():
        location = WorldMap.query.filter_by(letter_coord=form.letter.data,number_coord=form.number.data,world=world.id).first()
        if location.race:
            flash("There is already a race at that location")
            return redirect(url_for('.single_race',race=race.id))
        location.race = race.id
        cult_religion = Orders.query.get(race.religion)
        if cult_religion:
            cult_religion.locations.append(location)
            db.session.add(cult_religion)
        db.session.add(location)
        db.session.commit()
        flash("Race has expanded")
        return redirect(url_for('.single_race',race=race.id))
    if remove_form.validate_on_submit():
        location = WorldMap.query.get(remove_form.support.data)
        location.race = 0
        cult_religion = Orders.query.get(race.religion)
        if cult_religion in location.orders.all():
            location.orders.remove(cult_religion)
            db.session.add(cult_religion)
        db.session.add(location)
        db.session.commit()
        flash("Race has been removed from"+location.coords())
        return redirect(url_for('.single_race',race=race.id))
    if advance_form.validate_on_submit():
        new_advance = RaceAdvances(race_id=race.id,text=advance_form.text.data)
        db.session.add(new_advance)
        db.session.commit()
        flash("Race has been granted a boon")
        return redirect(url_for('.single_race',race=race.id))
        
    if advance_remove.validate_on_submit():
        advance = RaceAdvances.query.get(advance_remove.support.data)
        db.session.delete(advance)
        db.session.commit()
        flash("race has lost a boon")
        return redirect(url_for('.single_race', race=race.id))
    return render_template("/game/single_race.html",
                            active_world=world,
                            race=race,
                            form = form,
                            remove = remove_form,
                            cities=cities,
                            advance_form=advance_form,
                            advance_remove=advance_remove,
                            advances=advances,
                            )

@game.route("/cities", methods=["GET", "POST"])
@login_required
#Found cities, build buildings
#Considering /cities/<cityid> page for buildings @advances
def cities_page():
    world = World.query.get(session['active_world'])
    if world is None:
        flash("You need to select a world before accessing this page")
        return redirect(url_for('.index'))
    races = Race.query.filter_by(world_id=world.id).all()
    cities = City.query.filter_by(world_id=world.id).all()
    return render_template("/game/cities.html",
                           active_world=world,
                           races=races,
                           cities=cities,
                           )

@game.route("/cities/<cityid>",methods=['GET','POST'])
@game.route('/cities/<cityid>/<int:page>', methods=['GET', 'POST'])
@login_required
def single_city(cityid,page=1):
    world = World.query.get(session['active_world'])
    city = City.query.get(cityid)
    player_owner = city.return_owner_player()
    world_owner = world.owner
    if city is None:
        flash("That doesn't exist")
        return redirect(url_for('.world_page'))
    if city.world_id != world.id:
        flash("That doesn't exist in the active world")
        return redirect(url_for('.world_page'))
    buildings = city.buildings.all()
    armies = city.armies.all()
    history = city.ret_history().paginate(page, POSTS_PER_PAGE, False)
    form = MakeCityBldg(prefix="citybldg")
    army_form = MakeArmy(prefix="army")
    new_owner = NewOwner_Form(prefix="new_owner")
    advance_form = HistoryEntry(prefix="advance")
    advance_remove = ArmySupportFrom(prefix="remove_adv")
    advances = city.advances.all()
    advance_list = []
    for advance in advances:
        advance_list.append([advance.id,advance.text])
    advance_remove.support.choices = advance_list
    races = world.races.all()
    race_list = []
    for race in races:
        if race.id != city.owned_by:
            race_list.append( [race.id, race.culture_name])
    new_owner.new_owner.choices = race_list
    destroy = Destroy_Form(prefix="destroy")
    if form.validate_on_submit():
        new_bldg = BldgCity(name=form.name.data,
                            desc = form.description.data,
                            built_in = city.id,
                            age_turn = world.age_turn(),
                            turn_built = world.total_turns,
                            )
        db.session.add(new_bldg)
        entry = form.name.data+" was built"
        new_history = CityHistory(cityid=city.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    entry=entry,
                                    )
        db.session.add(new_history)
        hist_text = form.name.data+" was built in "+city.name
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        db.session.commit()
        flash("You built a building!")
        return redirect(url_for(".single_city",cityid=city.id))
    if army_form.validate_on_submit():
        race_controlling = city.owned_by
        player_id = Race.query.get(race_controlling).creator
        new_army = Armies(name=army_form.name.data,
                          location = city.location,
                          army = army_form.army.data,
                          home_city = city.id,
                          owner = player_id,
                          world = world.id,
                          home_culture= city.owned_by,
                          supported_from = city.id,
                          )
        db.session.add(new_army)
        entry = army_form.name.data+" was raised for "+User.query.get(player_id).name
        new_history = CityHistory(cityid=city.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    entry=entry,
                                    )
        db.session.add(new_history)
        hist_text = new_army.army_navy()+" "+new_army.name+" was raised in "+city.name
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        db.session.commit()
        flash("You built an army!")
        return redirect(url_for(".single_city",cityid=city.id))
    if new_owner.validate_on_submit():
        new_owner = new_owner.new_owner.data
        armies = city.armies.all()
        for army in armies:
            army.supported_from = 0
            db.session.add(army)
        city.owned_by = new_owner
        db.session.add(city)
        entry = city.name+" at "+city.return_location().coords()+" became controlled by the "+Race.query.get(new_owner).culture_name
        new_history = CityHistory(cityid=city.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    entry=entry,
                                    )
        db.session.add(new_history)
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=entry,)
        db.session.add(world_history)
        db.session.commit()
        flash(city.name+" has a new owner!")
        return redirect(url_for('.single_city',cityid=city.id))
    if destroy.validate_on_submit():
        city.is_alive = 0
        city.owned_by = 0
        city.destroyed_in = world.age_turn()
        armies = city.armies.all()
        for army in armies:
            army.supported_from = 0
            db.session.add(army)
        orders = city.orders.all()
        for order in orders:
            db.session.delete(order)
        db.session.add(city)
        entry = city.name+" at "+city.return_location().coords()+" was made into Ruins"
        new_history = CityHistory(cityid=city.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    entry=entry,
                                    )
        db.session.add(new_history)
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=entry,)
        db.session.add(world_history)
        db.session.commit()
        flash("You have destroyed "+city.name+" and all it contained! It lies in ruins.")
        return redirect(url_for(".cities_page"))
    if advance_form.validate_on_submit():
        new_advance = CityAdvances(city_id = city.id,
                                    text=advance_form.text.data)
        db.session.add(new_advance)
        entry = advance_form.text.data+" was developed"
        new_history = CityHistory(cityid=city.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    entry=entry,
                                    )
        db.session.add(new_history)
        hist_text = advance_form.text.data+" was developed in "+city.name
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        db.session.commit()
        return redirect(url_for('.single_city',cityid=city.id))
        
    if advance_remove.validate_on_submit():
        advance = CityAdvances.query.get(advance_remove.support.data)
        entry = "The secrets of "+advance.text+" was lost"
        new_history = CityHistory(cityid=city.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    entry=entry,
                                    )
        db.session.add(new_history)
        hist_text = "The city of "+city.name+" has lost the secrets of "+advance.text
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        db.session.delete(advance)
        
        db.session.commit()
        flash("Lost advance for city")
        return redirect(url_for('.single_city',cityid=city.id))
                          
    return render_template("/game/single_city.html",
                           active_world=world,
                           city=city,
                           form=form,
                           army_form=army_form,
                           buildings=buildings,
                           armies=armies,
                           new_owner=new_owner,
                           destroy=destroy,
                           history=history,
                           advances=advances,
                           advance_form=advance_form,
                           advance_remove=advance_remove,
                           player_owner = player_owner,
                           world_owner = world_owner,
                           )

@game.route("/orders",methods=['GET','POST'])
@login_required
#Create orders. Perhaps subpage for expanding/removing?
def orders_page():
    world = World.query.get(session['active_world'])
    if world is None:
        flash("You need to select a world before accessing this page")
        return redirect(url_for('.index'))
    players = world.players.all()
    form = MakeOrder()
    player_list = []
    if current_user.id == world.owner:
        for player in players:
            player_list.append([player.id,player.name])
    else:
        player_list.append([current_user.id,current_user.name])
    form.owner.choices= player_list
    races = Race.query.filter_by(world_id=world.id).all()
    orders = Orders.query.filter_by(world=world.id).all()
    
    if form.validate_on_submit():
        points = current_user.return_points_obj(world.id)
        if points.points < point_costs[world.age]['Create Order']:
            flash("You do not have enough points for this")
            return redirect(url_for(".orders_page"))
        new_order = Orders(name=form.name.data,
                           owner=form.owner.data,
                           description=form.description.data,
                           world=world.id,
                           type=form.type.data,)
        db.session.add(new_order)
        hist_text = User.query.get(form.owner.data).name+" has founded the "+new_order.name+", a "+new_order.order_type()+" order"
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        points.points -= point_costs[world.age]['Create Order']
        db.session.add(points)
        db.session.commit()
        flash("You have made a new order")
        return redirect(url_for(".orders_page"))
    return render_template("/game/orders.html",
                           active_world=world,
                           players=players,
                           races = races,
                           orders=orders,
                           form = form,
                           User=User,
                           found_order_cost = point_costs[world.age]['Create Order'],)

@game.route("/orders/<order>/", methods=['GET','POST'])
@login_required
def single_order(order):
    order = Orders.query.get(order)
    world = World.query.get(session['active_world'])
    if order is None:
        flash("That doesn't exist")
        return redirect(url_for('.world_page'))
    if order.world != world.id:
        flash("That doesn't exist in the active world")
        return redirect(url_for('.world_page'))
    destroyform = Destroy_Form(prefix="destroy")
    expand = UpdateLocation(prefix="expand")
    
    cities = City.query.filter_by(world_id=world.id,is_alive=1)
    city_list = []
    for each in Order_City.query.filter_by(order_id=order.id).all():
        city_list.append(each.return_city()) 
        
    city_expand = ArmySupportFrom(prefix="city")
    choices = []
    for city in cities:
        if not city in city_list:
            choices.append([city.id,city.name+": "+city.return_location().coords()])
    city_expand.support.choices = choices
    remove_city=ArmySupportFrom(prefix="cityremove")
    choices = []
    for city in cities:
        if city in city_list:
            choices.append([city.id,city.name+": "+city.return_location().coords()])
    remove_city.support.choices=choices
    remove = ArmySupportFrom(prefix="remove")
    choices = []
    locations = order.locations.all()
    for location in locations:
        choices.append([location.id,location.coords()])
    remove.support.choices = choices
    if destroyform.validate_on_submit():
        name = order.name
        order.is_alive = 0
        db.session.add(order)
        db.session.commit()
        flash("You have destroyed "+name+"!")
        return redirect(url_for(".orders_page"))
    if remove_city.validate_on_submit():
        city_id = remove_city.support.data
        print(city_id)
        order_city = Order_City.query.filter_by(order_id=order.id,city_id=city_id).first()
        print(order_city)
        db.session.delete(order_city)
        db.session.commit()
        flash("Order has left the city")
        return redirect(url_for(".single_order",order=order.id))
    if expand.validate_on_submit():
        location = WorldMap.query.filter_by(letter_coord=expand.letter.data,number_coord=expand.number.data,world=world.id).first()
        if location in order.locations:
            flash("Order is already in that location")
            return redirect(url_for(".single_order",order=order.id))
        order.locations.append(location)
        db.session.add(order)
        db.session.commit()
        flash("You have expanded an order")
        return redirect(url_for(".single_order",order=order.id))
    if city_expand.validate_on_submit():
        city_id = city_expand.support.data
        check = Order_City.query.filter_by(city_id=city_id,order_id=order.id).all()
        if check:
            flash("This order already exists in this city")
            return redirect(url_for(".single_order",order=order.id))
        new_link = Order_City(order_id = order.id,city_id=city_id)
        db.session.add(new_link)
        db.session.commit()
        flash("You have expanded to a city!")
        return redirect(url_for(".single_order",order=order.id))
    if remove.validate_on_submit():
        location = WorldMap.query.get(remove.support.data)
        order.locations.remove(location)
        db.session.add(order)
        db.session.commit()
        flash("You have contracted the order")
        return redirect(url_for(".single_order",order=order.id))
    
    return render_template("/game/single_order.html",
                            active_world=world,
                            order=order,
                            destroyform=destroyform,
                            expand=expand,
                            remove=remove,
                            locations=locations,
                            cities = city_list,
                            city_expand=city_expand,
                            remove_city=remove_city,
                            )

@game.route("/avatars",methods=['GET','POST'])
@login_required
#Create an avatar! Should build a 'create race' button here for that ability
#Should that be checked by player..
def avatars_page():
    world = World.query.get(session['active_world'])
    if world is None:
        flash("You need to select a world before accessing this page")
        return redirect(url_for('.index'))
    form = MakeAvatar()
    players = world.players.all()
    player_list = []
    if current_user.id == world.owner:
        for player in players:
            player_list.append([player.id,player.name])
    else:
        player_list.append([current_user.id,current_user.name])
    form.god.choices = player_list
    avatars = Avatars.query.filter_by(world=world.id).all()
    if form.validate_on_submit():
        points = current_user.return_points_obj(world.id)
        if points.points < point_costs[world.age]['Create Avatar']:
            flash("You do not have enough points for this")
            return redirect(url_for(".avatars_page"))
        new_avatar = Avatars(name = form.name.data,
                            owner = form.god.data,
                            location = WorldMap.query.filter_by(letter_coord=form.letter.data,number_coord=form.number.data,world=world.id).first().id,
                            description = form.description.data,
                            age_turn = world.age_turn(),
                            abs_turn= world.total_turns,
                            world = world.id
                            )
        db.session.add(new_avatar)
        hist_text = User.query.get(new_avatar.owner).name+" has spawned an avatar named "+new_avatar.name
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        points.points -= point_costs[world.age]['Create Avatar']
        db.session.add(points)
        db.session.commit()
        flash("You have made a new avatar!")
        return redirect(url_for(".avatars_page"))
    return render_template("/game/avatars.html",
                           active_world=world,
                           form=form,
                           players=players,
                           avatars=avatars,
                           cost = point_costs[world.age]['Create Avatar'],
                           )

@game.route("/avatars/<avatar_id>",methods=['GET','POST'])
@login_required
def single_avatar(avatar_id):
    world = World.query.get(session['active_world'])
    avatar = Avatars.query.get(avatar_id)
    if avatar is None:
        flash("That doesn't exist")
        return redirect(url_for('.world_page'))
    if avatar.world != world.id:
        flash("That doesn't exist in the active world")
        return redirect(url_for('.world_page'))
    destroy_form = Destroy_Form()
    new_location = UpdateLocation()
    if destroy_form.validate_on_submit():
        name = avatar.name
        db.session.delete(avatar)
        db.session.commit()
        flash("You've destroyed "+name)
        return redirect(url_for(".avatars_page"))
    if new_location.validate_on_submit():
        location = WorldMap.query.filter_by(letter_coord=new_location.letter.data,number_coord=new_location.number.data,world=world.id).first().id
        avatar.location = location
        db.session.add(avatar)
        db.session.commit()
        flash("You've updated the location")
        return redirect(url_for(".single_avatar",avatar_id=avatar_id))
    return render_template("/game/single_avatar.html",
                           active_world=world,
                           avatar=avatar,
                           destroyform=destroy_form,
                           location=new_location,
                           )

@game.route("/prov",methods=['GET','POST'])
@login_required
#For things like walls, bridges, farmland, forts
def prov_buildings_page():
    world = World.query.get(session['active_world'])
    buildings = BldgProv.query.filter_by(world_in=world.id).all()
    races = Race.query.filter_by(world_id=world.id).all()
    return render_template("/game/provbldg.html",
                           active_world=world,
                           buildings=buildings,)

@game.route("/prov/<bldg>",methods=['GET','POST'])
def single_provbldg(bldg):
    world = World.query.get(session['active_world'])
    building = BldgProv.query.get(bldg)
    if building is None:
        flash("That doesn't exist")
        return redirect(url_for('.world_page'))
    if building.world_in != world.id:
        flash("That doesn't exist in the active world")
        return redirect(url_for('.world_page'))
    newownerform = NewOwner_Form()
    race_list = []
    races = world.races.all()
    for race in races:
        if race.id != building.owned_by:
            race_list.append( [race.id, race.culture_name])
    newownerform.new_owner.choices = race_list
    destroyform = Destroy_Form()
    if newownerform.validate_on_submit():
        new_owner = newownerform.new_owner.data
        building.owned_by = new_owner
        db.session.add(building)
        hist_text = building.owner_name()+" have taken control over "+building.name+" at "+building.return_location().coords()
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        db.session.commit()
        flash("Changed Ownership")
        return redirect(url_for('.single_provbldg',bldg=building.id))
    if destroyform.validate_on_submit():
        if destroyform.destroy.data:
            building.is_alive = 0
            building.owned_by = 0
            building.destroyed_in = world.age_turn()
            db.session.add(building)
            hist_text = building.name+" at "+building.return_location().coords()+" has been made into ruins!"
            world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
            db.session.add(world_history)
            db.session.commit()
            flash("You destroyed "+building.name+"! It lies in ruins.")
        return redirect(url_for('.prov_buildings_page'))
    return render_template("/game/single_provbldg.html",
                           active_world=world,
                           building=building,
                           newownerform = newownerform,
                           destroyform = destroyform,
                           )

@game.route("/events",methods=['GET', 'POST'])
@login_required
#For when events are played
def events_page():
    form = MakeEvent()
    world = World.query.get(session['active_world'])
    players = world.players.all()
    player_list = []
    if current_user.id == world.owner:
        for player in players:
            player_list.append([player.id,player.name])
    else:
        player_list.append([current_user.id,current_user.name])
    form.played_by.choices = player_list
    events = world.event.all()
    remove_event = RemoveEvent(prefix="remove")
    remove_event_list = []
    for event in events:
        if event.duration > 0:
            remove_event_list.append([event.id,event.event_info])
    remove_event.played_by.choices = player_list
    remove_event.removal.choices = remove_event_list
    if form.validate_on_submit():
        new_event = Events(location = WorldMap.query.filter_by(letter_coord=form.letter.data,number_coord=form.number.data,world=world.id).first().id,
                          event_info=form.event_info.data,
                          played_by=form.played_by.data,
                          world=world.id,
                          age_turn = world.age_turn(),
                          abs_turn = world.total_turns,
                          duration = form.duration.data,
                          )
        db.session.add(new_event)
        hist_text = new_event.event_info+" in "+new_event.return_location().coords()+". Played by: "+new_event.playedby_name()
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        db.session.commit()
        flash("You played a new event")
        return redirect(url_for('.events_page'))
    if remove_event.validate_on_submit():
        event = Events.query.get(remove_event.removal.data)
        event.duration = 0
        hist_text = event.event_info+" in "+event.return_location().coords()+" has been removed by "+User.query.get(remove_event.played_by.data).name+"!"
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text)
        db.session.add(world_history)
        db.session.add(event)
        db.session.commit()
        flash("Event has been removed!")
        return redirect(url_for(".events_page"))
    return render_template("/game/events.html",
                           active_world=world,
                           form=form,
                           events=events,
                           players=players,
                           remove_event=remove_event,)

@game.route("/military",methods=['GET', 'POST'])
@login_required
#Create armies and navies
#Seperate control page per?
def military_page():
    world = World.query.get(session['active_world'])
    armies = world.armies.all()
    return render_template("/game/military.html",
                           active_world=world,
                           armies=armies
                           )

@game.route("/army/<armyid>",methods=['GET','POST'])
@login_required
def single_army(armyid):
    world = World.query.get(session['active_world'])
    army = Armies.query.get(armyid)
    if army is None:
        flash("That doesn't exist")
        return redirect(url_for('.world_page'))
    if army.world != world.id:
        flash("That doesn't exist in the active world")
        return redirect(url_for('.world_page'))
    form=UpdateLocation()
    rename=Rename()
    support=ArmySupportFrom()
    cities = City.query.filter_by(owned_by=army.home_culture).all()
    citychoice = []
    for each in cities:
        if each.is_alive:
            if each.id != army.supported_from:
                citychoice.append([each.id, each.name])
    support.support.choices = citychoice
    if form.validate_on_submit():
        number = form.number.data
        letter = form.letter.data
        army.location = WorldMap.query.filter_by(letter_coord=letter,number_coord=number,world=world.id).first().id
        db.session.add(army)
        db.session.commit()
        flash("New location for army")
        return redirect(url_for(".single_army",armyid=army.id))
    if rename.validate_on_submit():
        new_name = rename.new_name.data
        army.name = new_name
        db.session.add(army)
        db.session.commit()
        flash("New name for army")
        return redirect(url_for(".single_army",armyid=army.id))
    if support.validate_on_submit():
        army.supported_from = support.support.data
        db.session.add(army)
        db.session.commit()
        flash(army.name+" supported from "+army.supporting_city())
        return redirect(url_for(".single_army",armyid=army.id))
    return render_template("/game/army.html",
                           active_world=world,
                           army=army,
                           form=form,
                           rename=rename,
                           cities=citychoice,
                           support=support,
                           )

@game.route("/army/<armyid>/disband")
@login_required
def disband_army(armyid):
    army = Armies.query.get(armyid)
    armyname = army.name
    army.is_alive=0
    db.session.add(army)
    hist_text = army.name+" has been disbanded"
    world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
    db.session.add(world_history)
    db.session.commit()
    flash("You have destroyed "+armyname+"!")
    return redirect(url_for('.military_page'))

@game.route("/map")
@login_required
def world_map():
    world = World.query.get(session['active_world'])
    letters = ["",]
    for i in range(world.size):
        letters.append(str(i))
    locations = WorldMap.query.filter_by(world=world.id).order_by(WorldMap.number_coord)
    return render_template("/game/mapflip.html",
                            active_world=world,
                            letters=letters,
                            worldmap=WorldMap,
                            locations=locations,
                            size=world.size,)

@game.route("/map/regen")
@login_required
def world_map_regen():
    world = World.query.get(session['active_world'])
    scale = 1/48.0
    base = randint(1,48274)
    letters = ["",]
    for i in range(50):
        letters.append(str(i))
    locations = WorldMap.query.filter_by(world=world.id).order_by(WorldMap.number_coord)
    for i in locations:
        coords = i.regen_coords()
        map_noise = snoise2(coords['x'] * scale, coords['y'] * scale, octaves=4, persistence=0.75,base=base)
        if map_noise < -0.10:
            terrain_result = ['W','water.png']
        elif 0.35 > map_noise >= 0.15:
            terrain_result = ['F', 'forest.png']
        elif 0.55 >= map_noise >= 0.35:
            terrain_result = ['H','hills.png']
        elif map_noise > 0.55:
            terrain_result = ['M','mountains.png']
        else:
            terrain_result = ['G','grassland.png']
        i.terrain = terrain_result[0]
        i.image = terrain_result[1]
        db.session.add(i)
    db.session.commit()
    return redirect(url_for('.world_map'))
        
    
@game.route("/map/<location_id>", methods=['GET','POST'])
@login_required
def single_location(location_id):
    world = World.query.get(session['active_world'])
    location = WorldMap.query.get(location_id)
    terrain_form = ChangeTerrain()
    terrain_options = [['G','grassland.png',"Grassland",],['W','water.png',"Water",],
    ['M','mountains.png',"Mountains",],['J','jungle.png',"Jungle",],['F','forest.png',"Forest",],['H','hills.png',"Hills",]]
    form_options = []
    for option in terrain_options:
        if location.terrain not in option:
            form_options.append([option[0],option[2]])
    terrain_form.terrain.choices = form_options
    if location is None:
        flash("That doesn't exist")
        return redirect(url_for('.world_page'))
    if location.world != world.id:
        flash("That doesn't exist in the active world")
        return redirect(url_for('.world_page'))
    race = location.return_race()
    city = location.return_live_city()
    events = location.events.all()
    armies = location.army.all()
    avatars = location.avatars.all()
    command_race_form = CommandRace()
    command_order_form = CommandOrder()
    commands = [
        [1,'Construct Provincial Building',],
        [2,'Expand',],
        ]
    command_order_form.command_list.choices = commands
    if race and not city:
        commands.append([3,'Found City'])
    command_race_form.command_list.choices = commands
    if command_race_form.validate_on_submit():
        order = command_race_form.command_list.data
        if order == 1:
            return redirect(url_for(".build_prov_buildings",location_id = location.id,builder_source="Command Race",))
        elif order == 2:
            flash("Command: Expand")
            return redirect(url_for(".single_location",location_id = location.id))
        elif order == 3:
            return redirect(url_for(".single_location_make_city",location_id = location.id))
        else:
            flash("Error occured")
            return redirect(url_for(".single_location",location_id = location.id))
    if command_order_form.validate_on_submit():
        command = command_order_form.command_list.data
        if command == 1:
            session['builder_source'] = "Command Order"
            return redirect(url_for(".build_prov_buildings",location_id = location.id,builder_source="Command Order",))
        elif command == 2:
            flash("Command: Expand")
            return redirect(url_for(".single_location",location_id = location.id))
        else:
            flash("Error occured")
            return redirect(url_for(".single_location",location_id = location.id))
    if terrain_form.validate_on_submit():
        for option in terrain_options:
            if terrain_form.terrain.data in option:
                location.terrain=option[0]
                location.image=option[1]
        db.session.add(location)
        db.session.commit()
        return redirect(url_for(".single_location",location_id = location.id))
    orders = location.orders.all()
    for i in orders:
        if current_user.id == i.owner:
            owns_present_order = True
            break
    return render_template("/game/single_location.html",
                            active_world=world,
                            location=location,
                            race=race,
                            city=city,
                            events=events,
                            armies=armies,
                            avatars=avatars,
                            terrain_form=terrain_form,
                            command_race_form=command_race_form,
                            command_order_form=command_order_form,
                            command_race_cost=point_costs[world.age]['Command Race'],
                            command_order_cost=point_costs[world.age]['Command Order'],
                            orders = orders,
                            owns_present_order = owns_present_order,
                            )

@game.route("/map/<location_id>/make-city/", methods=['GET','POST'])
@login_required
def single_location_make_city(location_id):
    world = World.query.get(session['active_world'])
    location = WorldMap.query.get(location_id)
    race = Race.query.get(location.race)
    form = MakeCity()
    points = current_user.return_points_obj(world.id)
    if points.points < point_costs[world.age]['Command Race']:
        flash("You don't have enough points for this action")
        return redirect(url_for(".single_location",location_id = location.id))
    if form.validate_on_submit():
        points = current_user.return_points_obj(world.id)
        if points.points < point_costs[world.age]['Command Race']:
            flash("You do not have enough points for this")
            return redirect(url_for(".single_location",location_id = location.id))
        if City.query.filter_by(location=location.id,is_alive=1).count():
            flash("there is already a living city at that location")
            return redirect(url_for(".single_location",location_id = location.id))
        if City.query.filter_by(world_id=world.id,name=form.name.data,is_alive=1).count():
            flash("There is already a living city by that name.")
            return redirect(url_for(".single_location_make_city",location_id = location.id))
        new_city = City( name = form.name.data,
                         world_id = world.id,
                         built_by = race.id,
                         owned_by = race.id,
                         location = location.id,
                         alignment=form.alignment.data,
                         age_turn = world.age_turn(),
                         turn_built = world.total_turns,
                         )
        db.session.add(new_city)
        hist_text = new_city.name+" was founded at "+location.coords()+" by the "+race.culture_name
        new_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(new_history)
        city = City.query.order_by(City.id.desc()).first()
        history = CityHistory(cityid=city.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    entry=hist_text,
                                    )
        db.session.add(history)
        points.points -= point_costs[world.age]['Command Race']
        db.session.add(points)
        db.session.commit()
        return redirect(url_for('.cities_page'))
    return render_template("/game/make_city.html",
                            active_world=world,
                            form = form,
                            coords = location.coords(),
                            race = race,
                            command_race_cost=point_costs[world.age]['Command Race'],
                            )
                            
@game.route("/map/<location_id>/make-prov-bldg", methods=['GET','POST'])
@login_required
#For things like walls, bridges, farmland, forts
def build_prov_buildings(location_id):
    world = World.query.get(session['active_world'])
    builder_source = request.args.get('builder_source')
    points = current_user.return_points_obj(world.id)
    cost = point_costs[world.age][builder_source]
    print(builder_source)
    print(cost)
    if points.points < cost:
        flash("You don't have enough points for this action")
        return redirect(url_for(".single_location",location_id = location_id))
    location = WorldMap.query.get(location_id)
    race = Race.query.get(location.race)
    buildings = BldgProv.query.filter_by(world_in=world.id).all()
    form = MakeProvBldg()
    if form.validate_on_submit():
        new_building = BldgProv(name = form.name.data,
                                built_by = race.id,
                                owned_by = race.id,
                                description = form.description.data,
                                location = location.id,
                                world_in = world.id,
                                age_turn = world.age_turn(),
                                turn_built = world.total_turns,
                                is_alive = 1,
                                )
        db.session.add(new_building)
        hist_text = "The "+new_building.builder_name()+" have built "+new_building.name+" at "+new_building.return_location().coords()
        world_history = WorldHistory(world=world.id,
                                    abs_turn=world.total_turns,
                                    age_turn=world.age_turn(),
                                    text=hist_text,)
        db.session.add(world_history)
        points.points -= cost
        db.session.add(points)
        db.session.commit()
        return redirect(url_for(".prov_buildings_page"))
    return render_template("/game/build_prov_bldg.html",
                           active_world=world,
                           form=form,
                           buildings=buildings,
                           race=race,
                           cost=cost,
                           )