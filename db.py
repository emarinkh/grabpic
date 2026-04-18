from sqlalchemy import create_engine, Column, String, Integer, Table, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many (images to faces)
image_face_association = Table(
    'image_face_association',
    Base.metadata,
    Column('image_id', String, ForeignKey('images.image_id')),
    Column('grab_id', String, ForeignKey('faces.grab_id'))
)

class Face(Base):
    __tablename__ = 'faces'
    grab_id = Column(String, primary_key=True)  # Unique face ID
    embedding = Column(String)  # 128D vector as string (or JSON)
    images = relationship("Image", secondary=image_face_association, back_populates="faces")

class Image(Base):
    __tablename__ = 'images'
    image_id = Column(String, primary_key=True)
    file_path = Column(String, unique=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    faces = relationship("Face", secondary=image_face_association, back_populates="images")

# DB Setup
engine = create_engine('sqlite:///grabpic.db')  # or postgres://...
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)