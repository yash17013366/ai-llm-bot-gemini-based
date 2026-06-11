"""
Standalone Gemini API diagnostic script.

Run from the backend directory:
    python test_gemini.py
"""

import importlib.metadata
import os
import sys
import traceback

from dotenv import load_dotenv

load_dotenv()

PROMPT = "Say Hello"
MODEL_CANDIDATES = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]


def print_section(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def check_environment() -> str:
    print_section("1. Environment Loading")
    api_key = os.getenv("GEMINI_API_KEY", "")
    print(f"GEMINI_API_KEY loaded: {'YES' if api_key else 'NO'}")
    print(f"Key length: {len(api_key)}")
    print(f"Key prefix (first 10 chars): {api_key[:10] if api_key else '(empty)'}")
    print(f"Key format: {'AQ.* authorization key' if api_key.startswith('AQ.') else 'Legacy AIzaSy* or other'}")
    return api_key


def check_legacy_sdk(api_key: str) -> None:
    print_section("2. Legacy SDK: google-generativeai")
    try:
        version = importlib.metadata.version("google-generativeai")
        print(f"Package: google-generativeai")
        print(f"Version: {version}")
    except importlib.metadata.PackageNotFoundError:
        print("Package google-generativeai is NOT installed")
        return

    import google.generativeai as genai

    model_name = MODEL_CANDIDATES[0]
    print(f"Model: {model_name}")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(PROMPT)
        print(f"Response: {response.text}")
        print("Status: SUCCESS")
    except Exception:
        print("Status: FAILED")
        traceback.print_exc()


def check_new_sdk(api_key: str) -> None:
    print_section("3. New SDK: google-genai")
    try:
        version = importlib.metadata.version("google-genai")
        print(f"Package: google-genai")
        print(f"Version: {version}")
    except importlib.metadata.PackageNotFoundError:
        print("Package google-genai is NOT installed")
        print("Install with: pip install google-genai")
        return

    from google import genai
    from google.genai import errors as genai_errors

    client = genai.Client(api_key=api_key)

    for model_name in MODEL_CANDIDATES:
        print(f"\nTrying model: {model_name}")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=PROMPT,
            )
            print(f"Response: {response.text}")
            print(f"Status: SUCCESS with model {model_name}")
            return
        except genai_errors.ClientError as exc:
            print(f"Status: FAILED for {model_name}")
            print(f"Error: {exc}")
        except Exception:
            print(f"Status: FAILED for {model_name}")
            traceback.print_exc()

    print("\nAll models failed with google-genai SDK")


def main() -> int:
    print_section("Gemini Integration Diagnostic")
    api_key = check_environment()

    if not api_key:
        print("\nERROR: GEMINI_API_KEY is missing from environment/.env")
        return 1

    check_legacy_sdk(api_key)
    check_new_sdk(api_key)

    print_section("Summary")
    if api_key.startswith("AQ."):
        print(
            "Your key uses the new AQ.* authorization format.\n"
            "The legacy google-generativeai SDK often returns:\n"
            "  401 ACCESS_TOKEN_TYPE_UNSUPPORTED\n"
            "Migrate to google-genai SDK for AQ.* keys."
        )
    else:
        print("Your key uses a legacy format. Either SDK may work.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
