import pytest
import numpy as np
import tempfile
import os
import h5py
from unittest.mock import Mock, patch

from oecon.decimation import decimate_raw_data, decimate_np_array, DecimationConfig
from open_ephys.analysis.recording import Recording, Continuous, ContinuousMetadata
from dh5io.create import create_dh_file
from dh5io.cont import validate_cont_group


class MockContinuous(Continuous):
    """Mock class that inherits from Continuous"""

    def __init__(self, samples, metadata):
        self.samples = samples
        self.metadata = metadata

    def get_samples(
        self,
        start_sample_index=0,
        end_sample_index=-1,
        selected_channels=None,
        selected_channel_names=None,
    ):
        """Mock get_samples method that returns data for the selected channel"""
        if selected_channel_names and self.metadata.channel_names:
            # Find the index of the selected channel
            channel_idx = self.metadata.channel_names.index(selected_channel_names[0])
            # Return samples for that channel (reshape to column vector)
            return self.samples[:, channel_idx : channel_idx + 1]
        return self.samples


class MockRecording(Recording):
    """Mock class that inherits from Recording"""

    def __init__(self, continuous_data_list):
        # Don't call super().__init__() to avoid complex initialization
        self._continuous = continuous_data_list
        self._events = None
        self._spikes = None

    @property
    def continuous(self):
        return self._continuous

    @continuous.setter
    def continuous(self, value):
        self._continuous = value

    @property
    def events(self):
        return self._events

    @property
    def spikes(self):
        return self._spikes

    # Implement abstract methods from Recording class
    def load_spikes(self, experiment_id=0, recording_id=0):
        pass

    def load_events(self, experiment_id=0, recording_id=0):
        pass

    def load_continuous(self, experiment_id=0, recording_id=0):
        pass

    def load_messages(self, experiment_id=0, recording_id=0):
        pass

    @staticmethod
    def detect_format(directory):
        return True

    def detect_recordings(self, mmap_timestamps=True):
        pass

    def read_sync_channel(self, experiment_id=0, recording_id=0):
        pass

    def read_stream_sync_channel(self, stream_name, experiment_id=0, recording_id=0):
        pass

    def __str__(self):
        return None

    def _get_experiments(self):
        return []

    def _get_recordings(self, experiment_id):
        return []

    def _get_processors(self, experiment_id, recording_id):
        return []

    def _get_streams(self, experiment_id, recording_id, processor_id):
        return []


class TestDecimateNpArray:
    """Tests for the decimate_np_array function"""

    def test_decimate_np_array_basic(self):
        """Test basic decimation functionality"""
        # Create test data
        np.random.seed(42)
        data = np.random.randn(1000, 2)

        # Test decimation
        result = decimate_np_array(
            data=data,
            downsampling_factor=10,
            filter_order=30,
            filter_type="fir",
            axis=0,
            zero_phase=True,
        )

        # Check that output is decimated
        assert result.shape[0] == data.shape[0] // 10
        assert result.shape[1] == data.shape[1]

    def test_decimate_np_array_different_factors(self):
        """Test decimation with different downsampling factors"""
        data = np.random.randn(1000, 1)

        for factor in [2, 5, 10, 20]:
            result = decimate_np_array(
                data=data,
                downsampling_factor=factor,
                filter_order=10,
                filter_type="fir",
                axis=0,
                zero_phase=True,
            )
            expected_length = data.shape[0] // factor
            assert result.shape[0] == expected_length

    def test_decimate_np_array_filter_types(self):
        """Test decimation with different filter types"""
        data = np.random.randn(500, 1)

        for ftype in ["fir", "iir"]:
            result = decimate_np_array(
                data=data,
                downsampling_factor=5,
                filter_order=20,
                filter_type=ftype,
                axis=0,
                zero_phase=True,
            )
            assert result.shape[0] == data.shape[0] // 5


class TestDecimationConfig:
    """Tests for DecimationConfig dataclass"""

    def test_decimation_config_defaults(self):
        """Test default values of DecimationConfig"""
        config = DecimationConfig()

        assert config.downsampling_factor == 30
        assert config.ftype == "fir"
        assert config.zero_phase
        assert config.filter_order == 600
        assert config.included_channel_names is None
        assert config.start_block_id == 2001
        assert config.scale_max_abs_to is None

    def test_decimation_config_custom_values(self):
        """Test DecimationConfig with custom values"""
        config = DecimationConfig(
            downsampling_factor=10,
            ftype="iir",
            zero_phase=False,
            filter_order=100,
            included_channel_names=["CH1", "CH2"],
            start_block_id=3000,
            scale_max_abs_to=np.int16(16383),
        )

        assert config.downsampling_factor == 10
        assert config.ftype == "iir"
        assert not config.zero_phase
        assert config.filter_order == 100
        assert config.included_channel_names == ["CH1", "CH2"]
        assert config.start_block_id == 3000
        assert config.scale_max_abs_to == np.int16(16383)

    def test_decimation_config_with_real_dh5file(self):
        """Test DecimationConfig integration with a real temporary DH5File"""
        # Create a temporary file for the DH5 file
        with tempfile.NamedTemporaryFile(suffix=".dh5", delete=False) as temp_file:
            temp_path = temp_file.name

        try:
            # Create a real DH5File using create_dh_file
            dh5file = create_dh_file(temp_path, overwrite=True, validate=True)

            try:
                # Create test data
                np.random.seed(42)
                test_samples = np.random.randn(1000, 2)  # 1000 samples, 2 channels

                # Create metadata and continuous data
                metadata = ContinuousMetadata(
                    channel_names=["CH1", "CH2"],
                    sample_rate=30000,
                    source_node_name="test_node",
                    source_node_id=100,
                    stream_name="test_stream",
                    num_channels=2,
                    bit_volts=[0.05, 0.05],
                )

                continuous = MockContinuous(samples=test_samples, metadata=metadata)
                recording = MockRecording([continuous])

                # Create config with custom values
                config = DecimationConfig(
                    downsampling_factor=10,
                    ftype="fir",
                    filter_order=30,
                    zero_phase=True,
                    included_channel_names=["CH1", "CH2"],
                    start_block_id=2001,
                )

                # Test that the config works with the actual decimate_raw_data function
                result_config = decimate_raw_data(config, recording, dh5file)

                # Verify the configuration was updated correctly
                assert result_config.downsampling_factor == 10
                assert result_config.ftype == "fir"
                assert result_config.zero_phase
                assert result_config.filter_order == 30
                assert result_config.included_channel_names == ["CH1", "CH2"]
                assert result_config.start_block_id == 2001

                # Verify that the function actually processed the channels
                assert result_config.included_channel_names == ["CH1", "CH2"]

                # Check that data was actually written to the DH5 file
                expected_decimated_length = (
                    test_samples.shape[0] // config.downsampling_factor
                )

                assert 2001 in dh5file.get_cont_group_ids()
                assert 2002 in dh5file.get_cont_group_ids()

                dh5file.get_cont_group_by_id(2001)
                cont_ch1 = dh5file.get_cont_group_by_id(2001)
                # validate_cont_group(cont_ch1)
                data = cont_ch1.get("DATA")
                assert data is not None
                assert data.size == expected_decimated_length

                # TODO: ...

            finally:
                # Close the DH5File properly
                dh5file.file.close()

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestDecimateRawDataIntegration:
    """Integration tests for decimate_raw_data function"""

    @patch("dhspec.cont.create_channel_info")
    @patch("dh5io.cont.create_cont_group_from_data_in_file")
    @patch("dh5io.operations.add_operation_to_file")
    @patch("dhspec.cont.create_empty_index_array")
    @patch("oecon.version.get_version_from_pyproject")
    def test_decimate_raw_data_basic(
        self,
        mock_version,
        mock_index_array,
        mock_add_operation,
        mock_create_cont_group,
        mock_channel_info,
    ):
        """Test basic functionality of decimate_raw_data"""
        # Setup mocks
        mock_version.return_value = "1.0.0"
        mock_index_array.return_value = np.array([0])
        mock_channel_info.return_value = {"test": "channel_info"}

        # Create test data
        np.random.seed(42)
        test_samples = np.random.randn(1000, 2)  # 1000 samples, 2 channels

        # Create mock metadata and continuous data
        metadata = ContinuousMetadata(
            channel_names=["CH1", "CH2"],
            sample_rate=30000,
            source_node_name="test_node",
            source_node_id=100,
            stream_name="test_stream",
            num_channels=2,
            bit_volts=[0.05, 0.05],
        )

        continuous = MockContinuous(samples=test_samples, metadata=metadata)
        recording = MockRecording([continuous])

        # Create mock DH5File
        mock_dh5file = Mock()
        mock_dh5file.file = Mock()

        # Create config
        config = DecimationConfig(
            downsampling_factor=10,
            ftype="fir",
            filter_order=30,
            zero_phase=True,
            start_block_id=2001,
        )

        # Call the function
        result_config = decimate_raw_data(config, recording, mock_dh5file)

        # Verify results
        assert result_config.included_channel_names == ["CH1", "CH2"]

        # Verify that the DH5 operations were called for each channel
        assert mock_create_cont_group.call_count == 2  # One for each channel
        assert mock_add_operation.call_count == 1

        # Verify channel info creation
        assert mock_channel_info.call_count == 2

    @patch("dhspec.cont.create_channel_info")
    @patch("dh5io.cont.create_cont_group_from_data_in_file")
    @patch("dh5io.operations.add_operation_to_file")
    @patch("dhspec.cont.create_empty_index_array")
    @patch("oecon.version.get_version_from_pyproject")
    def test_decimate_raw_data_channel_selection(
        self,
        mock_version,
        mock_index_array,
        mock_add_operation,
        mock_create_cont_group,
        mock_channel_info,
    ):
        """Test decimate_raw_data with specific channel selection"""
        # Setup mocks
        mock_version.return_value = "1.0.0"
        mock_index_array.return_value = np.array([0])
        mock_channel_info.return_value = {"test": "channel_info"}

        # Create test data
        np.random.seed(42)
        test_samples = np.random.randn(500, 3)  # 500 samples, 3 channels

        # Create mock metadata and continuous data
        metadata = ContinuousMetadata(
            channel_names=["CH1", "CH2", "CH3"],
            sample_rate=30000,
            source_node_name="test_node",
            source_node_id=100,
            stream_name="test_stream",
            num_channels=3,
            bit_volts=[0.05, 0.05, 0.05],
        )

        continuous = MockContinuous(samples=test_samples, metadata=metadata)
        recording = MockRecording([continuous])

        # Create mock DH5File
        mock_dh5file = Mock()
        mock_dh5file.file = Mock()

        # Create config with specific channel selection
        config = DecimationConfig(
            downsampling_factor=5,
            included_channel_names=["CH1", "CH3"],  # Only process 2 out of 3 channels
            start_block_id=2001,
        )

        # Call the function
        result_config = decimate_raw_data(config, recording, mock_dh5file)

        # Verify results
        assert result_config.included_channel_names == ["CH1", "CH3"]

        # Verify that the DH5 operations were called only for selected channels
        assert mock_create_cont_group.call_count == 2  # Only CH1 and CH3
        assert mock_add_operation.call_count == 1

    def test_decimate_raw_data_no_continuous_data(self):
        """Test decimate_raw_data raises assertion error when no continuous data"""
        # Create recording with no continuous data
        recording = MockRecording([])
        recording.continuous = None

        # Create mock DH5File
        mock_dh5file = Mock()

        # Create config
        config = DecimationConfig()

        # Should raise assertion error
        with pytest.raises(AssertionError, match="No continuous data found"):
            decimate_raw_data(config, recording, mock_dh5file)

    @patch("dhspec.cont.create_channel_info")
    @patch("dh5io.cont.create_cont_group_from_data_in_file")
    @patch("dh5io.operations.add_operation_to_file")
    @patch("dhspec.cont.create_empty_index_array")
    @patch("oecon.version.get_version_from_pyproject")
    def test_decimate_raw_data_multiple_continuous_streams(
        self,
        mock_version,
        mock_index_array,
        mock_add_operation,
        mock_create_cont_group,
        mock_channel_info,
    ):
        """Test decimate_raw_data with multiple continuous streams"""
        # Setup mocks
        mock_version.return_value = "1.0.0"
        mock_index_array.return_value = np.array([0])
        mock_channel_info.return_value = {"test": "channel_info"}

        # Create test data for two streams
        np.random.seed(42)
        test_samples1 = np.random.randn(300, 2)  # Stream 1: 2 channels
        test_samples2 = np.random.randn(300, 1)  # Stream 2: 1 channel

        # Create mock metadata and continuous data for stream 1
        metadata1 = ContinuousMetadata(
            channel_names=["A1", "A2"],
            sample_rate=30000,
            source_node_name="node1",
            source_node_id=101,
            stream_name="stream1",
            num_channels=2,
            bit_volts=[0.05, 0.05],
        )
        continuous1 = MockContinuous(samples=test_samples1, metadata=metadata1)

        # Create mock metadata and continuous data for stream 2
        metadata2 = ContinuousMetadata(
            channel_names=["B1"],
            sample_rate=30000,
            source_node_name="node2",
            source_node_id=102,
            stream_name="stream2",
            num_channels=1,
            bit_volts=[0.1],
        )
        continuous2 = MockContinuous(samples=test_samples2, metadata=metadata2)

        # Create recording with multiple streams
        recording = MockRecording([continuous1, continuous2])

        # Create mock DH5File
        mock_dh5file = Mock()
        mock_dh5file.file = Mock()

        # Create config
        config = DecimationConfig(downsampling_factor=3)

        # Call the function
        result_config = decimate_raw_data(config, recording, mock_dh5file)

        # Verify results
        assert result_config.included_channel_names == ["A1", "A2", "B1"]

        # Verify that the DH5 operations were called for all channels across all streams
        assert mock_create_cont_group.call_count == 3  # A1, A2, B1
        assert mock_add_operation.call_count == 1
