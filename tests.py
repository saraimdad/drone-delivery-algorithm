
from bruteForceDrone import Drone, Environment, Package, Coordinate, Delivery


def test_successful_delivery():
    p1 = Package(ID=1, location=Coordinate(1, 10),
                 weight=5, quantity=1, priority=7)
    p2 = Package(ID=2, location=Coordinate(-2, -20),
                 weight=6, quantity=1, priority=6)
    d1 = Drone("Drone1", 40, 25, 2000, 1.5, 600, 2.5)
    envioron = Environment(5, 60)
    packages = [p1, p2]
    deliv = Delivery(d1, packages, envioron)
    deliv.deliver()
    # assert deliv.deliver() == "Delivery completed successfully."


def test_failed_delivery_due_to_battery():
    p1 = Package(ID=1, location=Coordinate(1, 10),
                 weight=5, quantity=1, priority=7)
    p2 = Package(ID=2, location=Coordinate(-2, -20),
                 weight=6, quantity=1, priority=6)
    d1 = Drone("Drone1", 40, 25, 50, 1.5, 600, 2.5)
    envioron = Environment(5, 60)
    packages = [p1, p2]
    deliv = Delivery(d1, packages, envioron)
    deliv.deliver()
    # assert deliv.deliver() == "Delivery failed due to insufficient battery."


# def test_failed_delivery_due_to_time():
#     p1 = Package(ID=1, location=Coordinate(1, 10),
#                  weight=5, quantity=1, priority=7)
#     p2 = Package(ID=2, location=Coordinate(-2, -20),
#                  weight=6, quantity=1, priority=6)
#     d1 = Drone("Drone1", 40, 25, 2000, 1.5, 600, 2.5)
#     envioron = Environment(5, 1)
#     packages = [p1, p2]
#     deliv = Delivery(d1, packages, envioron)
#     deliv.deliver()
    # assert deliv.deliver() == "Delivery failed due to insufficient time."


def test_failed_delivery_no_packages():
    d1 = Drone("Drone1", 40, 25, 2000, 1.5, 600, 2.5)
    envioron = Environment(5, 60)
    packages = []
    deliv = Delivery(d1, packages, envioron)
    deliv.deliver()
    # assert deliv.deliver() == "No packages to deliver."


def test_failed_delivery_heavy_package():
    p1 = Package(ID=1, location=Coordinate(1, 10),
                 weight=50, quantity=1, priority=7)
    p2 = Package(ID=2, location=Coordinate(-2, -20),
                 weight=60, quantity=1, priority=6)
    d1 = Drone("Drone1", 40, 25, 2000, 1.5, 600, 2.5)
    envioron = Environment(5, 60)
    packages = [p1, p2]
    deliv = Delivery(d1, packages, envioron)
    deliv.deliver()
    # assert deliv.deliver() == "Delivery failed: package too heavy for drone."


def main():
    test_successful_delivery()
    print('\n'*5, "Test Successful delivery", '\n'*5)
    test_failed_delivery_due_to_battery()
    print('\n'*5, "Test Failed delivery due to battery", '\n'*5)
    # test_failed_delivery_due_to_time()
    # print('\n'*5, "All tests passed successfully.", '\n'*5)
    test_failed_delivery_no_packages()
    print('\n'*5, "Test Failed delivery no packages", '\n'*5)
    try:
        test_failed_delivery_heavy_package()
        print('\n'*5, "Test Failed delivery heavy package", '\n'*5)
    except:
        print("Test Failed delivery heavy package")


if __name__ == "__main__":
    main()
