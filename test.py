from dotenv import load_dotenv
from openai import OpenAI
import json
import gradio as gr
import os
import requests
from pypdf import PdfReader
from flask import Flask, render_template , request , jsonify 
import sqlite3
from flask_api_key import APIKeyManager

app = Flask(__name__)
mgr = APIKeyManager(app)

my_key = mgr.create('MY_FIRST_KEY')
print(my_key.secret)

