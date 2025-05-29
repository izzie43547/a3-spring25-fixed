import unittest
import json
from ds_protocol import (
    format_auth_message,
    format_direct_message,
    format_fetch_request,
    extract_json,
    is_valid_response,
    DSPProtocolError
)

class TestDSProtocol(unittest.TestCase):
    def test_format_auth_message(self):
        """Test formatting of authentication message.

        Verifies that the format_auth_message function correctly formats
        the authentication message with the provided username and password.
        """
        # Test data
        username = "testuser"
        password = "testpass"
        expected = '{"authenticate": {"username": "testuser", "password": "testpass"}}'
        
        # Verify formatting
        self.assertEqual(format_auth_message(username, password), expected)
        
        # Test with special characters
        username_special = "user@name"
        password_special = "pass!word123"
        expected_special = '{"authenticate": {"username": "user@name", "password": "pass!word123"}}'
        self.assertEqual(format_auth_message(username_special, password_special), expected_special)

    def test_format_direct_message(self):
        """Test formatting of direct message.

        Verifies that the format_direct_message function correctly formats
        the message with all required fields including timestamp.
        """
        # Test data
        token = "test-token"
        recipient = "recipient"
        message = "Hello, World!"
        result = json.loads(format_direct_message(token, recipient, message))
        
        # Verify message structure
        self.assertEqual(result["token"], token)
        self.assertEqual(result["directmessage"]["recipient"], recipient)
        self.assertEqual(result["directmessage"]["message"], message)
        self.assertIn("timestamp", result["directmessage"])
        
        # Verify timestamp is valid
        timestamp = float(result["directmessage"]["timestamp"])
        self.assertTrue(isinstance(timestamp, float))
        self.assertGreater(timestamp, 0)
        
        # Test with special characters
        message_special = "Hello, World!\nHow are you?"
        result_special = json.loads(format_direct_message(token, recipient, message_special))
        self.assertEqual(result_special["directmessage"]["message"], message_special)

    def test_format_fetch_request(self):
        """Test formatting of fetch request.

        Verifies that the format_fetch_request function correctly formats
        fetch requests for both 'all' and 'unread' types, and raises
        DSPProtocolError for invalid types.
        """
        # Test data
        token = "test-token"
        
        # Test 'all' fetch type
        result_all = json.loads(format_fetch_request(token, 'all'))
        self.assertEqual(result_all["token"], token)
        self.assertEqual(result_all["fetch"], "all")
        
        # Test 'unread' fetch type
        result_unread = json.loads(format_fetch_request(token, 'unread'))
        self.assertEqual(result_unread["fetch"], "unread")
        
        # Test invalid fetch type
        with self.assertRaises(DSPProtocolError):
            format_fetch_request(token, 'invalid')
        
        # Test case sensitivity
        with self.assertRaises(DSPProtocolError):
            format_fetch_request(token, 'ALL')
        
        with self.assertRaises(DSPProtocolError):
            format_fetch_request(token, 'UnRead')

    def test_extract_json_valid(self):
        """Test extracting valid JSON response"""
        test_json = '''
        {
            "response": {
                "type": "ok",
                "message": "Success",
                "token": "test-token",
                "messages": [{"message": "test", "from": "user"}]
            }
        }
        '''
        response = extract_json(test_json)
        self.assertEqual(response.type, "ok")
        self.assertEqual(response.message, "Success")
        self.assertEqual(response.token, "test-token")
        self.assertEqual(len(response.messages), 1)

    def test_extract_json_invalid(self):
        """Test extracting invalid JSON response"""
        with self.assertRaises(DSPProtocolError):
            extract_json("invalid json")
        
        with self.assertRaises(DSPProtocolError):
            extract_json('{"not_response": {}}')

    def test_is_valid_response(self):
        """Test response validation"""
        valid_response = type('obj', (object,), {'type': 'ok'})
        invalid_response = type('obj', (object,), {'type': 'error'})
        self.assertTrue(is_valid_response(valid_response))
        self.assertFalse(is_valid_response(invalid_response))
        self.assertFalse(is_valid_response(None))

if __name__ == '__main__':
    unittest.main()
