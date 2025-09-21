# file: web_interface.py
from flask import Flask, request, render_template_string, session, redirect, url_for, jsonify
from main import execute_command
import os

app = Flask(__name__)
# A secret key is required for Flask session management
app.secret_key = os.urandom(24)

# List of all available commands for autocompletion
AVAILABLE_COMMANDS = ["ls", "cd", "pwd", "mkdir", "rm", "monitor", "help", "clear", "exit"]

HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Python Web Shell</title>
  <style>
    body {
      font-family: 'Consolas', 'Monaco', monospace;
      background: #1a1a1a;
      color: #00ff00;
      padding: 20px;
      margin: 0;
      display: flex;
      flex-direction: column;
      height: 100vh;
      box-sizing: border-box;
    }
    .terminal-output {
      flex-grow: 1;
      overflow-y: auto;
      border: 1px solid #333;
      padding: 10px;
      background: #000;
      margin-bottom: 10px;
      white-space: pre-wrap;
      word-wrap: break-word;
      box-shadow: 0 0 10px rgba(0,255,0,0.3);
    }
    .input-line {
      display: flex;
      align-items: center;
      color: #00ff00;
    }
    .prompt {
      margin-right: 5px;
      white-space: nowrap;
    }
    input[type=text] {
      flex-grow: 1;
      padding: 8px;
      background: #000;
      color: #00ff00;
      border: none;
      outline: none;
      font-family: 'Consolas', 'Monaco', monospace;
      font-size: 1em;
    }
    .initial-message {
        color: #eee;
        margin-bottom: 10px;
    }
    .output-line {
        color: #eee;
    }
  </style>
</head>
<body>
  <div class="terminal-output" id="terminalOutput">
    <div class="initial-message">Simple Python Web Shell. Use Arrow Keys for history, Tab for autocomplete.</div>
    {% for entry in session.get('history', []) %}
      <div class="input-line"><span class="prompt">>></span>{{ entry.command }}</div>
      <div class="output-line">{{ entry.output }}</div>
    {% endfor %}
  </div>

  <div class="input-line">
    <span class="prompt">>></span>
    <input type="text" id="commandInput" autofocus onkeydown="handleInput(event)" placeholder="">
  </div>

  <script>
    const commandInput = document.getElementById('commandInput');
    const terminalOutput = document.getElementById('terminalOutput');
    
    // --- Command History Logic ---
    const commandHistory = {{ command_history_json | safe }};
    let historyIndex = commandHistory.length;

    // --- Autocomplete State ---
    let lastSuggestions = [];
    let suggestionIndex = 0;

    terminalOutput.scrollTop = terminalOutput.scrollHeight;

    function handleInput(event) {
      const key = event.key;

      if (key === 'Enter') {
        event.preventDefault();
        const command = commandInput.value;
        if (command.trim() !== '') {
          submitCommand(command);
        }
      } else if (key === 'ArrowUp') {
        event.preventDefault();
        if (historyIndex > 0) {
          historyIndex--;
          commandInput.value = commandHistory[historyIndex];
          commandInput.setSelectionRange(commandInput.value.length, commandInput.value.length);
        }
      } else if (key === 'ArrowDown') {
        event.preventDefault();
        if (historyIndex < commandHistory.length - 1) {
          historyIndex++;
          commandInput.value = commandHistory[historyIndex];
          commandInput.setSelectionRange(commandInput.value.length, commandInput.value.length);
        } else {
          historyIndex = commandHistory.length;
          commandInput.value = '';
        }
      } else if (key === 'Tab') {
        event.preventDefault();
        handleAutocomplete();
      } else {
        // Reset autocomplete state if user types something else
        lastSuggestions = [];
        suggestionIndex = 0;
      }
    }

    function submitCommand(command) {
      const form = document.createElement('form');
      form.method = 'post';
      form.style.display = 'none';
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'command';
      input.value = command;
      form.appendChild(input);
      document.body.appendChild(form);
      form.submit();
    }
    
    async function handleAutocomplete() {
        const text = commandInput.value;
        if (lastSuggestions.length > 1) {
            suggestionIndex = (suggestionIndex + 1) % lastSuggestions.length;
            const parts = text.split(' ');
            parts[parts.length - 1] = lastSuggestions[suggestionIndex];
            commandInput.value = parts.join(' ');
            return;
        }

        const response = await fetch('/autocomplete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text: text})
        });
        const data = await response.json();
        const suggestions = data.suggestions;

        if (suggestions.length > 0) {
            lastSuggestions = suggestions;
            suggestionIndex = 0;
            const parts = text.split(' ');
            parts[parts.length - 1] = suggestions[0];
            commandInput.value = parts.join(' ');

            if (suggestions.length > 1) {
                const outputDiv = document.createElement('div');
                outputDiv.className = 'output-line';
                outputDiv.textContent = suggestions.join('   ');
                terminalOutput.appendChild(outputDiv);
                terminalOutput.scrollTop = terminalOutput.scrollHeight;
            }
        }
    }
  </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if 'history' not in session:
        session['history'] = []

    if request.method == "POST":
        command = request.form.get("command", "")
        output = ""

        if command:
            stripped_command = command.strip().lower()

            if stripped_command == "clear":
                session['history'] = []
                session.modified = True
                return redirect(url_for('index'))

            elif stripped_command == "exit":
                output = "Cannot exit the web server. Use 'clear' to clear history."

            elif stripped_command == "help":
                output = (
                    "Available commands:\\n"
                    "  ls, cd, pwd, mkdir, rm, monitor, clear, help, exit"
                )
            else:
                output = execute_command(command)
            
            if not session['history'] or session['history'][-1]['command'] != command:
                 session['history'].append({'command': command, 'output': output})

            session.modified = True
        return redirect(url_for('index'))

    command_history_list = [entry['command'] for entry in session.get('history', [])]
    return render_template_string(HTML_TEMPLATE, command_history_json=command_history_list)

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    data = request.json
    text = data.get('text', '')
    parts = text.split(' ')
    suggestions = []

    try:
        if len(parts) <= 1:
            token = parts[0]
            suggestions = [cmd for cmd in AVAILABLE_COMMANDS if cmd.startswith(token)]
        else:
            token = parts[-1]
            path = '.'
            if '/' in token or '\\' in token:
                path = os.path.dirname(token)
                token = os.path.basename(token)
            
            if not os.path.exists(path):
                return jsonify({'suggestions': []})

            items = os.listdir(path)
            for item in items:
                if item.startswith(token):
                    full_path = os.path.join(path, item)
                    if os.path.isdir(full_path):
                        suggestions.append(item + '/')
                    else:
                        suggestions.append(item)
    except Exception:
        pass
    
    return jsonify({'suggestions': sorted(suggestions)})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)