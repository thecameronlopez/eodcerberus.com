confirm = input("Restart DB? [y]:[n]: ")
if confirm.lower() == "y":

    print("Importing extensions")
    from app import create_app
    from app.extensions import db
    from app.models.base import Base

    print("creating application")
    app = create_app()
    print("creating app context")
    with app.app_context():
        print("emptying DB")
        Base.metadata.drop_all(bind=db.engine)
        print("initializing db")
        Base.metadata.create_all(bind=db.engine)

    print("DB has been reset!")
else:
    print("See ya later, aligator!")