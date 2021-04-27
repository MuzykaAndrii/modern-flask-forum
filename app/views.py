from flask import render_template, url_for, redirect, request, flash, abort
from app import app

@app.route('/')
def index():
    return "Hello world"