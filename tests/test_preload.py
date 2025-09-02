"""Tests for ASR model preloading functionality."""
import unittest
from unittest.mock import Mock, patch
import time


class TestModelPreloading(unittest.TestCase):
    """Test ASR model preloading during initialization."""
    
    @patch('faster_whisper.WhisperModel')
    def test_model_loads_on_initialization(self, mock_whisper):
        """Test that model is loaded during initialization, not on first transcribe."""
        mock_model_instance = Mock()
        mock_whisper.return_value = mock_model_instance
        
        from presstalk.engine.fwhisper_backend import FasterWhisperBackend
        
        # Create backend - this should trigger model loading
        backend = FasterWhisperBackend(model="tiny")
        
        # Verify model was loaded during initialization
        mock_whisper.assert_called_once_with("tiny")
        self.assertIsNotNone(backend._model)
        self.assertEqual(backend._model, mock_model_instance)
    
    @patch('numpy.frombuffer')
    @patch('faster_whisper.WhisperModel')
    def test_transcribe_is_fast_after_initialization(self, mock_whisper, mock_frombuffer):
        """Test that transcribe is fast after initialization (no lazy loading)."""
        mock_model_instance = Mock()
        mock_whisper.return_value = mock_model_instance
        
        # Mock transcribe to return segments
        mock_segment = Mock()
        mock_segment.text = "hello world"
        mock_model_instance.transcribe.return_value = ([mock_segment], Mock())
        
        # Mock numpy array conversion properly
        mock_int16_array = Mock()
        mock_float32_array = Mock()
        mock_final_array = Mock()
        mock_int16_array.astype.return_value = mock_float32_array
        mock_frombuffer.return_value = mock_int16_array
        # Mock the division operation
        type(mock_float32_array).__truediv__ = Mock(return_value=mock_final_array)
        
        from presstalk.engine.fwhisper_backend import FasterWhisperBackend
        
        backend = FasterWhisperBackend(model="tiny")
        
        # Reset mock to count calls during transcribe
        mock_whisper.reset_mock()
        
        # Call transcribe - should not trigger additional model loading
        result = backend.transcribe(b"dummy_audio", sample_rate=16000, language="en", model="tiny")
        
        # Model should not be loaded again during transcribe
        mock_whisper.assert_not_called()
        
        # Should return expected result
        self.assertEqual(result, "hello world")
    
    @patch('builtins.print')
    @patch('faster_whisper.WhisperModel')
    def test_progress_display_during_loading(self, mock_whisper, mock_print):
        """Test that progress is displayed during model loading."""
        mock_model_instance = Mock()
        mock_whisper.return_value = mock_model_instance
        
        from presstalk.engine.fwhisper_backend import FasterWhisperBackend
        
        # Create backend with progress display
        backend = FasterWhisperBackend(model="small", show_progress=True)
        
        # Verify progress messages were printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        progress_found = any("Loading ASR model" in call for call in print_calls)
        ready_found = any("Ready!" in call for call in print_calls)
        
        self.assertTrue(progress_found, f"No progress messages found in: {print_calls}")
        self.assertTrue(ready_found, f"No ready message found in: {print_calls}")
    
    @patch('builtins.print')
    @patch('faster_whisper.WhisperModel')
    def test_error_handling_with_progress(self, mock_whisper, mock_print):
        """Test that error messages are displayed when model loading fails."""
        mock_whisper.side_effect = RuntimeError("Model download failed")
        
        from presstalk.engine.fwhisper_backend import FasterWhisperBackend
        
        # Create backend with progress display - should raise error
        with self.assertRaises(RuntimeError) as cm:
            FasterWhisperBackend(model="small", show_progress=True)
        
        self.assertIn("Failed to load model 'small'", str(cm.exception))
        
        # Verify error message was printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        failed_found = any("FAILED" in call for call in print_calls)
        self.assertTrue(failed_found, f"No FAILED message found in: {print_calls}")


if __name__ == '__main__':
    unittest.main()