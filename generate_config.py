import os

os.makedirs(".streamlit", exist_ok=True)

config_content = """
[theme]
base = "light"
primaryColor = "#1e3a8a"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f0f0"
textColor = "#000000"
"""

with open(".streamlit/config.toml", "w") as config_file:
    config_file.write(config_content.strip())

print("✅ Created .streamlit/config.toml with custom sidebar background!")
