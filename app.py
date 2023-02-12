# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
director_ns = api.namespace('director')
genre_ns = api.namespace('genre')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_shcema = MovieSchema()
movies_schema = MovieSchema(many=True)


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id and genre_id:
            movie = db.session.query(Movie).filter(
                Movie.director_id == director_id, Movie.genre_id == genre_id).all()
            return movies_schema.dump(movie), 200
        elif director_id:
            movie = db.session.query(Movie).filter(
                Movie.director_id == director_id).all()
            return movies_schema.dump(movie), 200
        elif genre_id:
            movie = db.session.query(Movie).filter(
                Movie.genre_id == genre_id).all()
            return movies_schema.dump(movie), 200
        return movies_schema.dump(Movie.query.all()), 200


@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return '', 404
        return movie_shcema.dump(movie), 200


@director_ns.route('/')
class DirectorsView(Resource):
    def post(self):
        new_director = request.json
        director = Director(**new_director)
        db.session.add(director)
        db.session.commit()
        return "", 201


@director_ns.route('/<int:uid>')
class DirectorView(Resource):
    def put(self, uid):
        director = Director.query.get(uid)
        if not director:
            return '', 404
        new_info = request.json
        director.id = new_info.get('id')
        director.name = new_info.get('name')
        db.session.add(director)
        db.session.commit()
        return '', 204

    def delete(self, uid):
        director = Director.query.get(uid)
        if not director:
            return '', 404
        db.session.delete(director)
        db.session.commit()
        return '', 204


@genre_ns.route('/')
class GenresView(Resource):
    def post(self):
        new_genre = request.json
        genre = Genre(**new_genre)
        db.session.add(genre)
        db.session.commit()
        return "", 201


@genre_ns.route('/<int:uid>')
class GenreView(Resource):
    def put(self, uid):
        genre = Genre.query.get(uid)
        if not genre:
            return '', 404
        new_info = request.json
        genre.id = new_info.get('id')
        genre.name = new_info.get('name')
        db.session.add(genre)
        db.session.commit()
        return '', 204

    def delete(self, uid):
        genre = Genre.query.get(uid)
        if not genre:
            return '', 404
        db.session.delete(genre)
        db.session.commit()
        return '', 204


if __name__ == '__main__':
    app.run(debug=True)
