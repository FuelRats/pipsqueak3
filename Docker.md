# Docker Support
MechaSqueak3 now has Docker support, and can be run from a Docker
container almost as easily as if run natively.

## Requirements
Docker. Obviously.
    - It must be able of running linux containers, we arn't targetting
    windows here.

Docker-compose - It should come shipped with your Docker install
    but if it is not, you will need to install it.


## Building the container
In order to use Mechasqueak within a container, you will need to build
    the container. Doing so is pretty streight forward.

1. clone the project down
        - no need to install dependencies or anything, this is handled
        in the next step
2. run `docker-compose build`
        - this builds the mecha3 container
        - you may be asked to grant Docker permission to access the
            drive you cloned mecha3 to, this is to allow mecha3 to write
            its logs back to non-volitile diskspace.
        - logs will be stored in `$PROJECT_ROOT/logs`
## Running mecha3
Once the container is built its pretty streight forward to running
    mechasqueak3.

It is advised to run the test suite first to ensure the build process
    did not do anything unexpected.

### Running the Test Suite
to run the test suite enter the following command into your terminal:
    ```docker-compose up tests```

### Running the Bot itself
to run the irc bot itself, enter the following command into your terminal
```docker-compose up mecha3```

## Default executable state of the container
By default, the mecha3 container will execute the test suite.

Running the container directly via
```docker run mecha3``` is identical to running the tests as described
    above.