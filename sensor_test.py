from time import sleep
from requests.exceptions import JSONDecodeError
from conftest import wait


def test_sanity(
        get_sensor_info,
        get_sensor_reading,
        get_sensor_methods,
        set_sensor_name,
        set_sensor_reading_interval,
        reset_sensor_to_factory,
        update_sensor_firmware,
        reboot_sensor,
):
    set_sensor_name("new_name")
    set_sensor_reading_interval(10)
    sensor_info = get_sensor_info()

    sensor_name = sensor_info.get("name")
    assert isinstance(sensor_name, str), "Sensor name is not a string"
    assert sensor_name == "new_name", "Sensor name was not set correctly"

    sensor_interval = sensor_info.get("reading_interval")
    assert isinstance(sensor_interval, int), "Sensor reading interval is not an int"

    sensor_hid = sensor_info.get("hid")
    assert isinstance(sensor_hid, str), "Sensor hid is not a string"

    sensor_model = sensor_info.get("model")
    assert isinstance(sensor_model, str), "Sensor model is not a string"

    sensor_firmware_version = sensor_info.get("firmware_version")
    assert isinstance(
        sensor_firmware_version, int
    ), "Sensor firmware version is not a string"

    sensor_reading_interval = sensor_info.get("reading_interval")
    assert isinstance(
        sensor_reading_interval, int
    ), "Sensor reading interval is not a string"

    sensor_reading = get_sensor_reading()
    assert isinstance(
        sensor_reading, float
    ), "Sensor doesn't seem to register temperature"

    print("Sanity test passed")


def test_reboot(get_sensor_info, reboot_sensor):
    """
    Steps:
        1. Get original sensor info.
        2. Reboot sensor.
        3. Wait for sensor to come back online.
        4. Get current sensor info.
        5. Validate that info from Step 1 is equal to info from Step 4.
    """
    print("Get original sensor info")
    sensor_info_before_reboot = get_sensor_info()

    print("Reboot sensor")
    reboot_response = reboot_sensor()
    assert reboot_response == "rebooting, will be back in 3 seconds", (
        "Sensor did not return proper text in response " "to reboot request"
    )

    print("Wait for sensor to come back online")
    sensor_info_after_reboot = wait(
        func=get_sensor_info,
        condition=lambda x: isinstance(x, dict),
        tries=10,
        timeout=1,
    )

    print("Validate that info from Step 1 is equal to info from Step 4")
    assert (
            sensor_info_before_reboot == sensor_info_after_reboot
    ), "Sensor info after reboot doesn't match original info"


def test_set_sensor_name(get_sensor_info, set_sensor_name):
    """
    1. Set sensor name to "new_name".
    2. Get sensor_info.
    3. Validate that current sensor name matches the name set in Step 1.
    """
    print("Set sensor name to 'new_name'")
    set_sensor_name("new_name")

    print("Get sensor info")
    sensor_info = get_sensor_info()

    print(
        f"Validate that current sensor name matches the name set in Step 1, current name is: {sensor_info['name']}"
    )
    assert sensor_info["name"] == "new_name", "Sensor name was not set correctly"


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
    print("Set sensor reading interval to 1")
    set_sensor_reading_interval(1)

    print("Get sensor info")
    sensor_info = get_sensor_info()

    print("Validate that sensor reading interval is set to interval from Step 1")
    assert (
            sensor_info["reading_interval"] == 1
    ), "Sensor reading interval was not set correctly"

    print("Get sensor reading")
    sensor_reading = get_sensor_reading()

    print("Wait for interval specified in Step 1")
    sleep(10)

    print("Get sensor reading")
    sensor_reading_after_interval = get_sensor_reading()

    print(
        f"Validate that reading from Step 4 doesn't equal reading from Step 6, current readings are: {sensor_reading} and {sensor_reading_after_interval}"
    )
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
    print("Get original sensor firmware version")
    sensor_info = get_sensor_info()
    original_firmware_version = sensor_info["firmware_version"]

    print("Request firmware update")
    update_sensor_firmware()

    print("Get current sensor firmware version")
    sleep(10)
    sensor_info = get_sensor_info()
    current_firmware_version = sensor_info["firmware_version"]

    print("Validate that current firmware version is +1 to original firmware version")
    assert current_firmware_version == original_firmware_version + 1, (
        "Sensor firmware version was not updated correctly"
    )

    print("Repeat steps 1-4 until sensor is at max_firmware_version - 1")
    print("Update sensor to max firmware version")
    while current_firmware_version < 14:
        print("Get original sensor firmware version")
        sensor_info = get_sensor_info()
        original_firmware_version = sensor_info["firmware_version"]

        print("Request firmware update")
        update_sensor_firmware()

        print("Get current sensor firmware version")
        sleep(10)
        sensor_info = get_sensor_info()
        current_firmware_version = sensor_info["firmware_version"]

        print("Validate that current firmware version is +1 to original firmware version")
        assert current_firmware_version == original_firmware_version + 1, (
            "Sensor firmware version was not updated correctly"
        )


"""
I don't delete this function because I understand it, most likely I will use this style in my tests as a beginner
    for i in range(10):
        print(f"Attempt {i + 1}")
        try:
            print("Get current sensor info")
            sensor_info_after_reboot = get_sensor_info()
            break
        except JSONDecodeError:
            print("could not get sensor info")
            pass
        print("Sleeping for 1 second")
        sleep(1)
"""