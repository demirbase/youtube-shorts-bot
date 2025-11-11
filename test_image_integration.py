#!/usr/bin/env python3
"""
Quick integration test for reddit_image_creator
Tests that it works with the same post_data structure used in main_v3.py
"""

from reddit_image_creator import create_reddit_post_image

# Simulate the post_data structure that main_v3.py would have
test_post_data = {
    'title': "What's the most interesting fact you know that sounds completely made up?",
    'body': 'I love learning random facts that seem too crazy to be true but are actually real. Share your favorites!',
    'subreddit': 'AskReddit',
    'url': 'https://reddit.com/r/AskReddit/test',
    'comments': [
        {
            'author': 'ScienceGeek42',
            'body': 'Honey never spoils. Archaeologists found 3000-year-old honey in Egyptian tombs that was still perfectly edible.'
        },
        {
            'author': 'SpaceFan88',
            'body': 'There are more possible iterations of a game of chess than there are atoms in the known universe.'
        },
        {
            'author': 'AnimalLover',
            'body': 'Octopuses have three hearts and blue blood. Two hearts pump blood to the gills, one pumps it to the rest of the body.'
        }
    ]
}

print("🧪 Testing reddit_image_creator integration...")
print("=" * 60)

# Test with the exact same call that main_v3.py uses
result = create_reddit_post_image(
    post_data=test_post_data,
    output_file="integration_test.png",
    width=1080,
    height=1920
)

if result:
    print()
    print("✅ Integration test PASSED!")
    print(f"   Image created successfully: {result}")
    print("   This confirms the image creator works with main_v3.py's data structure")
else:
    print()
    print("❌ Integration test FAILED")
    print("   Image creator returned None")
