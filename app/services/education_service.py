from typing import List, Optional
from app.schemas.education_schema import ArticleOut
from fastapi import HTTPException

ARTICLES = [
    {
        "id": "1",
        "title": "Understanding Your Carbon Footprint: The Basics",
        "excerpt": "What exactly is a carbon footprint? Learn about the key factors that contribute to your personal emissions and why tracking them matters.",
        "category": "Basics",
        "date": "Jan 12, 2025",
        "readTime": "5 min",
        "slug": "basics-of-carbon-footprint",
        "imageColor": "bg-green-200",
        "body": "A carbon footprint measures the total greenhouse gas emissions caused directly and indirectly by an individual or organization. It includes emissions from transportation, energy use, food, and shopping.\n\nUnderstanding your carbon footprint helps you identify where you can reduce emissions and make more sustainable choices. Tracking this number encourages long-term behavior change and supports climate-friendly habits.",
    },
    {
        "id": "2",
        "title": "10 Simple Ways to Reduce Home Energy Use",
        "excerpt": "Cut down on your electricity bill and your emissions with these practical tips for a more energy-efficient home.",
        "category": "Lifestyle",
        "date": "Jan 15, 2025",
        "readTime": "7 min",
        "slug": "reduce-home-energy",
        "imageColor": "bg-blue-200",
        "body": "Small upgrades can make a big difference in household energy consumption. Start by switching to LED lighting and unplugging devices that are not in use.\n\nImproving insulation, using smart thermostats, and choosing energy-efficient appliances will lower energy demand and reduce your home emissions over time.",
    },
    {
        "id": "3",
        "title": "The Future of Sustainable Transportation",
        "excerpt": "From electric vehicles to high-speed rail, explore how the way we move is changing to protect our planet.",
        "category": "Technology",
        "date": "Jan 18, 2025",
        "readTime": "8 min",
        "slug": "sustainable-transportation",
        "imageColor": "bg-indigo-200",
        "body": "Sustainable transportation is about shifting away from fossil fuels and choosing low-impact mobility options. Electric vehicles, public transit, cycling, and walking are all part of the solution.\n\nAdvances in batteries, smart routing, and infrastructure investment are making cleaner travel more affordable and convenient for communities around the world.",
    },
    {
        "id": "4",
        "title": "Plant-Based Diet: Myth vs. Reality",
        "excerpt": "Does eating less meat really help the environment? We dive into the data behind food production and emissions.",
        "category": "Food",
        "date": "Jan 20, 2025",
        "readTime": "6 min",
        "slug": "plant-based-diet-impact",
        "imageColor": "bg-orange-200",
        "body": "Food production is responsible for a significant portion of global emissions, especially in the livestock sector. Reducing meat consumption can lower your personal footprint and reduce pressure on land and water resources.\n\nA plant-based diet can be healthy, satisfying, and more sustainable when it includes a variety of fruits, vegetables, whole grains, legumes, and nuts.",
    },
    {
        "id": "5",
        "title": "How Carbon Offsetting Works",
        "excerpt": "Can you really pay to erase your emissions? Understanding the mechanics and ethics of carbon offset projects.",
        "category": "Basics",
        "date": "Jan 22, 2025",
        "readTime": "10 min",
        "slug": "how-offsets-work",
        "imageColor": "bg-teal-200",
        "body": "Carbon offsetting allows individuals and businesses to invest in projects that reduce or remove emissions elsewhere. Good offsets support verified renewable energy, reforestation, or community-based clean cooking programs.\n\nWhile offsets can be part of a broader climate strategy, they should be used alongside direct emissions reductions rather than as a substitute.",
    },
    {
        "id": "6",
        "title": "Zero Waste Living for Beginners",
        "excerpt": "A practical guide to reducing waste in your daily life, from grocery shopping to composting.",
        "category": "Lifestyle",
        "date": "Jan 25, 2025",
        "readTime": "6 min",
        "slug": "zero-waste-beginners",
        "imageColor": "bg-yellow-200",
        "body": "Zero waste living starts with reducing what you consume and choosing reusable alternatives. Small changes like carrying a water bottle, using cloth bags, and composting food scraps can cut landfill waste dramatically.\n\nAdopting a minimalist approach to packaging and gifts helps you save money and support a circular economy.",
    },
]


def get_all_articles() -> List[ArticleOut]:
    return [ArticleOut(**item) for item in ARTICLES]


def get_article_by_slug(slug: str) -> ArticleOut:
    normalized_slug = slug.strip().lower()
    for item in ARTICLES:
        if item["slug"].strip().lower() == normalized_slug:
            return ArticleOut(**item)
    raise HTTPException(status_code=404, detail="Article not found")
