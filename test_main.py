import json
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock

# Import the module under test
import main


class TestSendTelegramMessage:
    """Tests for send_telegram_message function."""

    def test_send_telegram_message_missing_token(self, capsys):
        """Should print warning when token is not set."""
        with patch.object(main, 'UPBIT_BOT_TOKEN', None):
            with patch.object(main, 'UPBIT_CHAT_ID', 'test_chat_id'):
                main.send_telegram_message("test message")
        
        captured = capsys.readouterr()
        assert "Telegram token or chat ID not set" in captured.out

    def test_send_telegram_message_missing_chat_id(self, capsys):
        """Should print warning when chat ID is not set."""
        with patch.object(main, 'UPBIT_BOT_TOKEN', 'test_token'):
            with patch.object(main, 'UPBIT_CHAT_ID', None):
                main.send_telegram_message("test message")
        
        captured = capsys.readouterr()
        assert "Telegram token or chat ID not set" in captured.out

    @patch('main.requests.post')
    def test_send_telegram_message_success(self, mock_post):
        """Should successfully send message to Telegram API."""
        mock_response = MagicMock()
        mock_response.text = '{"ok": true}'
        mock_post.return_value = mock_response

        with patch.object(main, 'UPBIT_BOT_TOKEN', 'test_token'):
            with patch.object(main, 'UPBIT_CHAT_ID', 'test_chat_id'):
                main.send_telegram_message("Hello World")

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert 'test_token' in call_args[0][0]
        assert call_args[1]['data']['chat_id'] == 'test_chat_id'
        assert call_args[1]['data']['text'] == 'Hello World'
        assert call_args[1]['data']['parse_mode'] == 'HTML'

    @patch('main.requests.post')
    def test_send_telegram_message_network_error(self, mock_post, capsys):
        """Should handle network errors gracefully."""
        mock_post.side_effect = Exception("Network error")

        with patch.object(main, 'UPBIT_BOT_TOKEN', 'test_token'):
            with patch.object(main, 'UPBIT_CHAT_ID', 'test_chat_id'):
                main.send_telegram_message("test message")

        captured = capsys.readouterr()
        assert "Telegram send failed" in captured.out


class TestFetchMarkets:
    """Tests for fetch_markets function."""

    @patch('main.requests.get')
    def test_fetch_markets_success(self, mock_get):
        """Should return sorted list of market codes."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"market": "KRW-BTC"},
            {"market": "KRW-ETH"},
            {"market": "KRW-ADA"},
        ]
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = main.fetch_markets()

        assert result == ["KRW-ADA", "KRW-BTC", "KRW-ETH"]
        mock_get.assert_called_once_with(
            main.UPBIT_API_URL,
            params={"isDetails": "false"},
            timeout=10
        )

    @patch('main.requests.get')
    def test_fetch_markets_empty_response(self, mock_get):
        """Should return empty list for empty API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = main.fetch_markets()

        assert result == []

    @patch('main.requests.get')
    def test_fetch_markets_api_error(self, mock_get, capsys):
        """Should return empty list and print error on API failure."""
        mock_get.side_effect = Exception("API timeout")

        result = main.fetch_markets()

        assert result == []
        captured = capsys.readouterr()
        assert "Error fetching markets" in captured.out

    @patch('main.requests.get')
    def test_fetch_markets_http_error(self, mock_get, capsys):
        """Should return empty list on HTTP error status."""
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("500 Server Error")
        mock_get.return_value = mock_response

        result = main.fetch_markets()

        assert result == []


class TestLoadPreviousState:
    """Tests for load_previous_state function."""

    def test_load_previous_state_file_not_found(self):
        """Should return empty list when state file doesn't exist."""
        with patch.object(main, 'STATE_FILE', 'nonexistent_file.json'):
            result = main.load_previous_state()
        
        assert result == []

    def test_load_previous_state_valid_json(self):
        """Should return list of markets from valid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(["KRW-BTC", "KRW-ETH"], f)
            temp_path = f.name

        try:
            with patch.object(main, 'STATE_FILE', temp_path):
                result = main.load_previous_state()
            
            assert result == ["KRW-BTC", "KRW-ETH"]
        finally:
            os.unlink(temp_path)

    def test_load_previous_state_corrupted_json(self, capsys):
        """Should return empty list and print warning for corrupted JSON."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("not valid json {{{")
            temp_path = f.name

        try:
            with patch.object(main, 'STATE_FILE', temp_path):
                result = main.load_previous_state()
            
            assert result == []
            captured = capsys.readouterr()
            assert "State file is corrupted" in captured.out
        finally:
            os.unlink(temp_path)


class TestSaveState:
    """Tests for save_state function."""

    def test_save_state_creates_file(self):
        """Should create state file with JSON content."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(main, 'STATE_FILE', temp_path):
                main.save_state(["KRW-BTC", "KRW-ETH", "KRW-ADA"])

            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data == ["KRW-BTC", "KRW-ETH", "KRW-ADA"]
        finally:
            os.unlink(temp_path)

    def test_save_state_empty_list(self):
        """Should save empty list correctly."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(main, 'STATE_FILE', temp_path):
                main.save_state([])

            with open(temp_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data == []
        finally:
            os.unlink(temp_path)


class TestFlaskRoutes:
    """Tests for Flask routes."""

    @pytest.fixture
    def client(self):
        """Create test client for Flask app."""
        main.app.config['TESTING'] = True
        with main.app.test_client() as client:
            yield client

    def test_home_route(self, client):
        """Should return running status message."""
        response = client.get('/')
        
        assert response.status_code == 200
        assert b"Upbit scanner running!" in response.data

    @patch('main.send_telegram_message')
    def test_test_alert_route(self, mock_send, client):
        """Should trigger test alert and return success message."""
        response = client.get('/test-alert')
        
        assert response.status_code == 200
        assert b"Test message sent!" in response.data
        mock_send.assert_called_once()
        assert "Test alert" in mock_send.call_args[0][0]


class TestStateRoundTrip:
    """Integration tests for state persistence."""

    def test_save_and_load_state(self):
        """Should save and load state correctly (round trip)."""
        markets = ["KRW-BTC", "KRW-ETH", "KRW-XRP", "KRW-ADA"]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name

        try:
            with patch.object(main, 'STATE_FILE', temp_path):
                main.save_state(markets)
                loaded = main.load_previous_state()
            
            assert loaded == markets
        finally:
            os.unlink(temp_path)
