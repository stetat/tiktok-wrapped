<h2> How to run the bot?** </h2>

Make sure you have python 3.9.6+ installed

Clone this repo: `git clone https://github.com/stetat/tiktok-wrapped.git`

Get into a newly cloned directory: `cd tiktok-wrapped`

Create a virtual environment `python -m venv .venv`

Activate virtual environment on Mac/Linux: `source .venv/bin/activate`, on Windows (PowerShell terminal): `.venv\Scripts\Activate.ps1`

Install dependencies: `pip install -r requirements.txt`

Create a new file called .env, inside that file, add two variables: `BOT_TOKEN="YOUR TELEGRAM BOT TOKEN"`

Open a new terminal (let's call it t2, whereas main terminal is t1) (Both t1 and t2 should have the virtual environment open)

In t1 write this command, to start fastApi server: `fastapi dev backend.py`

In t2 write this command, to start Telegram bot logic: `python bot.py`

You can now move to your telegram bot and interact with it


<hr>

<h2>What can this bot do?</h2>
<pre>
1. Accept a JSON file with Tiktok Data and return statistics.
</pre>


