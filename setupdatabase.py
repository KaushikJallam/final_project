from main import  User,Trip,Ride,db, app,Quotation

def show_users():
    with app.app_context():
        all_users = User.query.all()

        for user in all_users:
            print(f"Username: {user.username},  Password : {user.password}, email: {user.email}, type: {user.user_type} , trip: {user.rides_as_passenger}")

def passenger_rides():
    with app.app_context():
        all_rides = Ride.query.all()

        for ride in all_rides:
                print("Ride ID:", ride.id)
                print("Passenger ID:", ride.passenger_id)
                print("Driver ID:", ride.driver_id)
                print("From Location:", ride.from_location)
                print("To Location:", ride.to_location)
                print("trip_id",ride.trip_id)
                print("Status",ride.status)
                print("---")





def see_quotations():
    with app.app_context():
        quotation = Quotation.query.all()
        for q in quotation:
            print("id",q.id)
            print("driver_id",q.driver_id)
            print("status",q.status)
            print("updatd status",q.status)
            print('check rides',q.rides)
        # quote = Quotation.query.get(24)
        # print(quote.rides)


def check_available_trips():
    with app.app_context():
        available_trips = Trip.query.all()
        print(f"Number of available trips: {len(available_trips)}")
        for trip in available_trips:
            print(f"Trip ID: {trip.id}, From: {trip.from_location}, To: {trip.to_location}")



# def show():
#     show_users()
#     passenger_rides()
#     check_available_trips()

if __name__ == '__main__':
    # show_users()
    # show()
    # check_available_trips()
    # passenger_rides()
    see_quotations()
