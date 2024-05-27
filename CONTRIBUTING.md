# PSNAWP CONTRIBUTING Guidelines

There are several ways you can contribute to this project. Here can some guidelines that can help you contribute to the project. Following this guideline will make it easier for me to work on your PR and get it merged asap.

## Setup Instructions

### 1. Install Poetry Python

This project uses [Poetry](https://python-poetry.org/docs/) for dependency management. Ensure you have Poetry installed before proceeding.

### 2. Install Dependencies

To install all dependencies, run:

```bash
poetry install
```

### 3. Activate the Virtual Environment

Activate the Poetry-managed virtual environment with the following command:

```bash
poetry shell
```
> Note: A lot of commands in this document will assume that you have activated virtual environment.

## Running Static Analysis, Formatting, and Linting
Before committing make sure to run static analysis, formatting, and linting. To run all of them execute the following command.

```bash
python3 pre_push.py
```

You may need to run it multiple times to make sure everything passes.

## Running Tests

If you made any change to code, it is important that you first run the test locally to make sure everything is working correctly. You should add new test if new methods are added. However, if you are not sure how to write test then at least make sure old tests are running.

### 1. Create a .env File
Create a .env file in the root directory of the project. This file will hold your environment variables. These env variables will be used during the execution of test.

Below is a template for the .env file:

```bash
NPSSO_CODE=<npsso-code>
USER_NAME=<your-username>
FRIEND_USER_NAME=<your-friend-username>
```

### 2. Run Tests
To run tests only, run the following command.

```bash
python3 pre_push.py -nu
```

## Reversing PlayStation API endpoints

You can also help by reversing PlayStation endpoint and documenting their behavior. In order to do that you need a rooted android phone, Android Studio, and couple of more tools. If you don't have rooted android phone use Android Studio virtual device to create one. Pick Android 11 (x86) image. The PlayStation apk is going to be armeabi-v7a, arm64-v8a and only Android 11 afaik supports installing ARM apks. Use [rootAVD](https://gitlab.com/newbit/rootAVD) to root this virtual device.

Once you have the rooted android phone follow the instructions from this article [Defeating Android Certificate Pinning with Frida](https://httptoolkit.com/blog/frida-certificate-pinning/). Once you follow all the instructions you should be able to see all the PlayStation API traffic on HTTP Toolkit. Document the endpoints like the params, request body, url, and so on.

Once you find all the details you can create an issue here and I'll keep them in mind for future releases of PSNAWP.

> Note: Make sure to redact all sensitive information before adding endpoint details to Github issue.
