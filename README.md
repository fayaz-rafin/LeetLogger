# LeetLogger

This Discord bot helps track and manage LeetCode problem-solving progress for users on your server. It allows users to log problems they've solved and view their ongoing streaks and past solutions.

## Features

- **Problem Tracking**: Users can record each LeetCode problem they solve.
- **Streak Tracking**: The bot tracks how many consecutive days a user has solved at least one problem.
- **Progress Overview**: Users can retrieve a list of all the problems they've solved along with their current streak.

## Setup

### Prerequisites

- Python 3.8 or higher
- Discord account and a Discord server where you have permissions to add bots.
- Supabase account for database services.

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/leetcode-tracker-bot.git
   cd leetcode-tracker-bot

2. **Install dependencies:**

```bash
python -m pip install -r requirements.txt
```

3. **Configure your environment variables:**
Create a .env file in the root directory and add the following:

```DISCORD_TOKEN=your_discord_bot_token_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_api_key_here
```

### Running the Bot
Start the bot by running:

`python main.py`

# Usage:
## Commands
-  !solve [problem_id] [problem_name]

Description: Record a problem as solved.
Usage: `!solve 1 Two Sum`
This command logs the problem and updates your daily streak.


- !progress
Description: Shows all the problems you have solved and your current streak.
Usage: `!progress`
The bot will respond with an embed listing each problem solved, the date solved, and your current streak.

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

### Fork the Project
Create your Feature Branch (git checkout -b feature/AmazingFeature)
Commit your Changes (git commit -m 'Add some AmazingFeature')
Push to the Branch (git push origin feature/AmazingFeature)
Open a Pull Request
License

Distributed under the MIT License. See LICENSE for more information.
