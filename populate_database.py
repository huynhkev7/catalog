import datetime

from setup_database import Base, Category, Item, User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

dumby_user = User(name="John Doe", email="jd123@gmail.com")

# populate initial categories
fruit_category = Category(name="Fruit")
session.add(fruit_category)

vegetables_category = Category(name="Vegetables")
session.add(vegetables_category)

protein_category = Category(name="Proteins")
session.add(protein_category)

grains_category = Category(name="Grains")
session.add(grains_category)

# populate initial items for each category
apple = Item(
        name="Apple",
        description="An apple is a sweet, " +
        "edible fruit produced by an apple tree.",
        category=fruit_category,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=dumby_user)
session.add(apple)

kale = Item(
        name="Kale",
        description="Kale or leaf cabbage are certain cultivars" +
        " of cabbage grown for their edible leaves.",
        category=vegetables_category,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=dumby_user)
session.add(kale)

tofu = Item(
        name="Tofu",
        description="Tofu, also known as bean curd, is a food cultivated" +
        " by coagulating soy milk and then pressing" +
        " the resulting curds into soft white blocks.",
        category=protein_category,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=dumby_user)
session.add(tofu)

rice = Item(
        name="Rice",
        description="Rice is the seed of the grass" +
        " species Oryza sativa or Oryza glaberrima.",
        category=grains_category,
        created_date=datetime.datetime.now(),
        updated_date=datetime.datetime.now(),
        user=dumby_user)
session.add(rice)

session.commit()
