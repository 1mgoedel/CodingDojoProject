from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models.event import Event
import requests
import googlemaps

gmaps = googlemaps.Client(key='AIzaSyC-3LQbnNmdFEoIt3nKfUFoOrB5REZhFXo')

@app.route('/events/new')
def new_sighting():
    return render_template('newEvent.html')

@app.route('/message/<int:user_id>/<int:event_id>/<location>', methods=['POST'])
def new_message(user_id, event_id, location):
    print("\ngot here\n")
    Event.leave_message(user_id, event_id, request.form['message'])
    result = f"/details/{event_id}/{location}"
    return redirect(result)


@app.route('/events/new/create', methods=['POST'])
def create_new_event():
    print("\nIn the create route\n")
    if not Event.validate_event(request.form):
        print("\nIn not validated\n")
        return redirect('/events/new')
    data = {
        "name": request.form['name'],
        "location": request.form['location'],
        "type": request.form['type'],
        "date": request.form['date'],
        "time": request.form['time'],
        "min_num_of_players": request.form['min_num_of_players'],
        "max_num_of_players": request.form['max_num_of_players'],
        "user_id": session['id']
    }
    Event.save(data)
    return redirect('/home')

@app.route('/search')
def searchEvent():
    count = []
    creators = Event.get_all_events_with_creator()
    events = Event.get_all_events_with_attendees()
    for i in range(len(events)):
        id = events[i]['id']
        count.append(Event.get_events_counts(id))
    return render_template('search.html', creators=creators, count=count, events=events)

@app.route('/search/sport', methods=['POST'])
def searchEventByType():
    count = []
    creators = Event.get_all_events_with_creator_for_type(request.form['sport'])
    events = Event.search_by_type(request.form['sport'])
    for i in range(len(events)):
        id = events[i]['id']
        count.append(Event.get_events_counts(id))
    return render_template('search.html', creators=creators, count=count, events=events)

@app.route('/attend/<int:event_id>')
def add_attendee(event_id):
    Event.add_attendee(session['id'], event_id)
    return redirect('/search')

@app.route('/details/<int:id>/<my_location>')
def details(id, my_location):
    print(f"\n\nMy location: {my_location}\n\n")
        # Use the Google Maps Geocoding API to get latitude and longitude of a location
    geocode_result = gmaps.geocode(my_location)
    print(f"\n\ngeocode_results: {geocode_result}\n\n")

    # Extract latitude and longitude
    lat = geocode_result[0]['geometry']['location']['lat']
    lng = geocode_result[0]['geometry']['location']['lng']

    print(f"\nlat: {lat}\n")
    print(f"\nlng: {lng}\n")

    from flask_app.models.user import User
    event = Event.get_an_event(id)
    creator = User.get_all_user_info(event[0]['user_id'])
    count = Event.count_attendees(id)
    messages = Event.get_messages_for_event(id)
    return render_template('eventDetails.html', event=event[0], creator=creator[0], count=count[0], messages=messages, lat=lat, lng=lng)

@app.route('/edit/<int:id>')
def edit_event(id):
    event = Event.get_an_event(id)

    return render_template('editEvent.html', event=event[0])

@app.route('/edit/<int:id>/action', methods=['POST'])
def editing(id):
    Event.update_event(request.form, id)
    location = request.form['location']
    return redirect(f'/details/{id}/{location}')