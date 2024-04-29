from conftest import wait, SensorInfo
import logging

log = logging.getLogger(__name__)


def test_sanity(get_sensor_info, get_sensor_reading):
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.name
    assert isinstance(sensor_name, str), "Sensor name is not a string"

    sensor_interval = sensor_info.reading_interval
    assert isinstance(sensor_interval, int), "Sensor reading interval is not an int"

    sensor_hid = sensor_info.hid
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.model
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.firmware_version
    assert isinstance(
        sensor_firmware_version, int
    ), "Sensor firmware version is not a string"

    sensor_reading_interval = sensor_info.reading_interval
    assert isinstance(
        sensor_reading_interval, int
    ), "Sensor reading interval is not a string"

    sensor_reading = get_sensor_reading()
    assert isinstance(
        sensor_reading, float
    ), "Sensor doesn't seem to register temperature"


def test_set_sensor_name(get_sensor_info, set_sensor_name):
    """
    1. Set sensor name to "new_name".
    2. Get sensor_info.
    3. Validate that current sensor name matches the name set in Step 1.
    """

    expected_name = "new_name"
    log.info(f"Set sensor name to {expected_name}")
    set_sensor_name(expected_name)

    log.info("Get sensor info")
    sensor_info = get_sensor_info()

    log.info(
        "Validate that current sensor name matches the name set in Step 1, current name is: {sensor_info.get("
        "'name')}"
    )
    assert sensor_info.name == expected_name, "Sensor didn't set its name correctly"


def test_reboot(get_sensor_info, reboot_sensor):
    """
    Steps:
        1. Get original sensor info.
        2. Reboot sensor.
        3. Wait for sensor to come back online.
        4. Get current sensor info.
        5. Validate that info from Step 1 is equal to info from Step 4.
    """
    log.info("Get original sensor info")
    sensor_info_before_reboot = get_sensor_info()

    log.info("Reboot sensor")
    reboot_response = reboot_sensor()
    assert (
            reboot_response == "rebooting"
    ), "Sensor did not return proper text in response to reboot request"

    log.info("Wait for sensor to come back online")
    sensor_info_after_reboot = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, SensorInfo),
        tries=10,
        timeout=1,
    )

    log.info("Validate that info from Step 1 is equal to info from Step 4")
    assert (
            sensor_info_before_reboot == sensor_info_after_reboot
    ), "Sensor info after reboot doesn't match sensor info before reboot"


def test_set_sensor_reading_interval(
        get_sensor_info, set_sensor_reading_interval, get_sensor_reading
):
    """
    1. Set sensor reading interval to 1.
    2. Get sensor info.
    3. Validate that sensor reading interval is set to interval from Step 1.
    4. Get sensor reading.
    5. Wait for interval specified in Step 1.
    6. Get sensor reading.
    7. Validate that reading from Step 4 doesn't equal reading from Step 6.
    """
    log.info("Set sensor reading interval to 1")
    interval = 1
    set_sensor_reading_interval(interval)

    log.info("Get sensor info")
    sensor_info = get_sensor_info()

    log.info("Validate that sensor reading interval is set to interval from Step 1")
    assert (
            sensor_info.reading_interval == interval
    ), "Sensor reading interval was not set correctly"

    log.info("Get sensor reading")
    sensor_reading = get_sensor_reading()

    log.info("Wait for interval specified in Step 1")

    log.info("Get sensor reading")
    sensor_reading_after_interval = wait(
        func=get_sensor_reading(),
        condition=lambda x: isinstance(x, SensorInfo),
        tries=15,
        timeout=interval,
    )

    log.info(f"Validate that reading from Step 4 doesn't equal reading from Step 6")
    assert (
            sensor_reading != sensor_reading_after_interval
    ), "Sensor reading interval is not working correctly"


# Максимальна версія прошивки сенсора -- 15,
def test_update_sensor_firmware(get_sensor_info, update_sensor_firmware):
    """
    1. Get original sensor firmware version.
    2. Request firmware update.
    3. Get current sensor firmware version.
    4. Validate that current firmware version is +1 to original firmware version.
    5. Repeat steps 1-4 until sensor is at max_firmware_version - 1.
    6. Update sensor to max firmware version.
    7. Validate that sensor is at max firmware version.
    8. Request another firmware update.
    9. Validate that sensor doesn't update and responds appropriately.
    10. Validate that sensor firmware version doesn't change if it's at maximum value.
    """

    firmware_version = "firmware_version"
    max_firmware_version = 15
    current_firmware_version = 0

    while current_firmware_version != max_firmware_version:
        log.info("1. Get current sensor firmware version")
        sensor_info = get_sensor_info()
        current_firmware_version = sensor_info.firmware_version

        log.info("2. Request firmware update")
        update_sensor_firmware()

        log.info("3. Get current sensor firmware version after update")
        sensor_info_after_update = wait(
            func=get_sensor_info,
            condition=lambda x: isinstance(x, SensorInfo),
            tries=15,
            timeout=1,
        )
        updated_firmware_version = sensor_info_after_update.firmware_version

        log.info(
            "4. Validate that current firmware version is +1 to original firmware version"
        )

        assert (
                updated_firmware_version == current_firmware_version + 1
        ), "Sensor firmware version was not updated correctly"

        current_firmware_version = updated_firmware_version

        if current_firmware_version == max_firmware_version:
            log.info("6. Update sensor to max firmware version")
            break
        log.info("5. Repeat steps 1-4 until sensor is at max_firmware_version - 1")

    log.info("7. Validate that sensor is at max firmware version")
    assert (
            current_firmware_version == max_firmware_version
    ), "Sensor firmware version not max"

    log.info("8. Request another firmware update")
    response_to_firmware_update_request = update_sensor_firmware()

    log.info("9. Validate that sensor doesn't update and responds appropriately")
    assert (
            response_to_firmware_update_request == "already at latest firmware version"
    ), "Sensor firmware version not max"

    log.info(
        "10. Validate that sensor firmware version doesn't change if it's at maximum value"
    )
    sensor_info_after_update = get_sensor_info()
    current_firmware_version = sensor_info_after_update.firmware_version
    assert (
            current_firmware_version == max_firmware_version
    ), "Sensor firmware version not max"


def test_set_empty_sensor_name(get_sensor_info, set_sensor_name):
    """
    Test Steps:
    1. Get original sensor name.
    2. Set sensor name to an empty string.
    3. Validate that sensor responds with an error.
    4. Get current sensor name.
    5. Validate that sensor name didn't change.
    """

    log.info("1. Get original sensor name")
    sensor_info = get_sensor_info()
    original_name = sensor_info.name

    log.info("2. Set sensor name to an empty string")
    empty_name = ""
    response_to_empty_name = set_sensor_name(empty_name)

    log.info("3. Validate that sensor responds with an error")
    assert response_to_empty_name == "error", "Sensor didn't respond with an error"

    log.info("4. Get current sensor name")
    sensor_info_after_empty_name = get_sensor_info()
    current_name = sensor_info_after_empty_name.name

    log.info("5. Validate that sensor name didn't change")
    assert current_name == original_name, "Sensor name changed when it shouldn't have"


def test_set_invalid_sensor_reading_interval(get_sensor_info, set_sensor_reading_interval):
    """
    Test Steps:
        1. Get original sensor reading interval.
        2. Set interval to < 1
        3. Validate that sensor responds with an error.
        4. Get current sensor reading interval.
        5. Validate that sensor reading interval didn't change.
    """

    log.info("1. Get original sensor reading interval")
    sensor_info = get_sensor_info()
    original_interval = sensor_info.reading_interval

    log.info("2. Set interval to < 1")
    invalid_interval = 0
    response_to_invalid_interval = set_sensor_reading_interval(invalid_interval)

    log.info("3. Validate that sensor responds with an error")
    assert response_to_invalid_interval == "error", "Sensor didn't respond with an error"

    log.info("4. Get current sensor reading interval")
    sensor_info_after_invalid_interval = get_sensor_info()
    current_interval = sensor_info_after_invalid_interval.reading_interval

    log.info("5. Validate that sensor reading interval didn't change")
    assert current_interval == original_interval, "Sensor reading interval changed when it shouldn't have"

