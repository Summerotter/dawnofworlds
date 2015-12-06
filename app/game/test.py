@game.route("/map/<location_id>/expand-order/<order_id>/",methods=['GET','POST'])
@login_required
def expand_order(location_id, order_id):
    world_check()
    world = World.query.get(session['active_world'])
    location = WorldMap.query.get(location_id)
    order = Orders.query.get(order_id)
    builder_source = session['builder_source']
    cost = point_costs[world.age][builder_source]
    points = current_user.return_points_obj(world.id)
    if not order:
        flash("Invalid resource")
        return redirect(url_for(".single_location",location_id = location.id))
       
    letter = location.letter_coord #X
    number = location.number_coord #Y
    neighbors = []
    if request.form:
        if points.points < cost:
            flash("Not enough points for that action")
            return redirect(url_for(".single_location",location_id = location.id))
        if 'location' in request.form:
            expand_target = location = WorldMap.query.get(request.form['location'])
            order.locations.append(expand_target)
            points.points -= cost
            db.session.add(points)
            db.session.add(expand_target)
            db.session.commit()
            return redirect(url_for(".single_location",location_id = expand_target.id))
    label_x = [letter-1,letter,letter+1]
    label_y = [number-1,number,number+1]
    print("Letter: ",letter)
    print("Number: ",number)
    neighbor_lands = []
    neighbors = [[[-1,-1,],[0,-1],[+1,-1]],
                 [[-1,0,],[0,0,],[+1,0]],
                [[-1,+1,],[0,+1],[+1,+1]],
                 ]
                 

    for row in neighbors:
        for item in row:
            
            y = item[0]+letter
            x = item[1]+number
            if x < 0 or y < 0:
                neighbor_lands.append(False)
            elif x == 0 and y == 0:
                neighbor_lands.append(location)
            elif x > world.size or y > world.size:
                neighbor_lands.append(False)
            else:
                neighbor = WorldMap.query.filter_by(letter_coord=y,number_coord=x,world=world.id).first()
                neighbor_lands.append(neighbor)

    return render_template("/game/expansion.html",
                            active_world=world,
                            locations = neighbor_lands,
                            letters = label_x,
                            label_y = label_y,
                            )