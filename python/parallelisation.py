import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


# region domain objects
@dataclass
class Storyboard:
    description: str
    scenes: list['Scene'] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class Scene:
    scene_id: int
    content: str
    search_queries: list['SearchQuery'] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class SearchQuery:
    query_text: str
    scene_id: int
    video_assets: list['VideoAsset'] = field(default_factory=list)
    error: Optional[str] = None


@dataclass
class VideoAsset:
    asset_id: str
    url: str
    relevance_score: float = 0.0
    reranked_score: Optional[float] = None
    error: Optional[str] = None


# endregion


# region simulated processing steps
async def generate_scenes_dspy(description: str) -> list[Scene]:
    """Simulate DSPy generating 5-10 scenes."""
    await asyncio.sleep(0.5)  # Simulate API latency
    num_scenes = 7  # In reality, DSPy decides this
    return [
        Scene(scene_id=i, content=f"Scene {i} for: {description[:30]}...")
        for i in range(num_scenes)
    ]


async def generate_search_queries_dspy(scene: Scene) -> list[SearchQuery]:
    """Simulate DSPy generating search queries for a scene."""
    await asyncio.sleep(0.3)  # Simulate API latency
    return [
        SearchQuery(query_text=f"Query {i} for scene {scene.scene_id}", scene_id=scene.scene_id)
        for i in range(3)  # Generate 3 queries per scene
    ]


async def search_api_call(query: SearchQuery) -> list[VideoAsset]:
    """Simulate search API returning video assets."""
    await asyncio.sleep(1.5)  # Simulate API latency
    # Simulate occasionally failing
    if query.query_text.endswith("1"):
        raise Exception(f"Search API error for query: {query.query_text}")

    return [
        VideoAsset(
            asset_id=f"asset_{query.scene_id}_{i}",
            url=f"https://example.com/video_{i}.mp4",
            relevance_score=0.8 - (i * 0.1),
        )
        for i in range(2)  # Return 2 assets per query
    ]


async def rerank_dspy(asset: VideoAsset, query: SearchQuery) -> VideoAsset:
    """Simulate DSPy reranking a video asset."""
    await asyncio.sleep(1.2)  # Simulate API latency
    asset.reranked_score = asset.relevance_score * 1.2  # Improve score
    return asset


# endregion


# region processing strategies
# region STRATEGY 1: Process one search query with error handling
async def process_search_query_safe(query: SearchQuery) -> SearchQuery:
    """Process a single search query: API call + rerank all results."""
    try:
        # Get video assets from search API
        assets = await search_api_call(query)

        # Rerank all assets in parallel
        rerank_tasks = [rerank_dspy(asset, query) for asset in assets]
        reranked_assets = await asyncio.gather(*rerank_tasks, return_exceptions=True)

        # Handle reranking errors
        for i, result in enumerate(reranked_assets):
            if isinstance(result, Exception):
                assets[i].error = str(result)
                print(f"⚠️  Reranking error for {assets[i].asset_id}: {result}")
            else:
                assets[i] = result

        query.video_assets = assets

    except Exception as e:
        query.error = str(e)
        print(f"⚠️  Search query error: {e}")

    return query


# endregion


# region STRATEGY 2: Process one scene with all its queries
async def process_scene_safe(scene: Scene) -> Scene:
    """Process a single scene: generate queries + search + rerank."""
    try:
        # Generate search queries for this scene
        scene.search_queries = await generate_search_queries_dspy(scene)

        # Process all search queries in parallel
        query_tasks = [process_search_query_safe(q) for q in scene.search_queries]
        scene.search_queries = await asyncio.gather(*query_tasks)

    except Exception as e:
        scene.error = str(e)
        print(f"⚠️  Scene {scene.scene_id} error: {e}")

    return scene


# endregion


# region STRATEGY 3: Process entire storyboard
async def process_storyboard(description: str) -> Storyboard:
    """
    Process entire storyboard with maximum parallelisation.

    Structure:
    1. Generate scenes (sequential - DSPy decides count)
    2. Process all scenes in parallel
       - For each scene: generate queries (sequential)
       - Process all queries in parallel
         - For each query: search API (sequential)
         - Rerank all assets in parallel
    """
    print(f"🎬 Starting storyboard: {description}\n")
    storyboard = Storyboard(description=description)

    # Step 1: Generate scenes (must be sequential as DSPy decides count)
    print("📝 Generating scenes...")
    storyboard.scenes = await generate_scenes_dspy(description)
    print(f"✓ Generated {len(storyboard.scenes)} scenes\n")

    # Step 2: Process all scenes in parallel
    print("🔄 Processing scenes in parallel...")
    scene_tasks = [process_scene_safe(scene) for scene in storyboard.scenes]
    storyboard.scenes = await asyncio.gather(*scene_tasks)

    # Report results
    print(f"\n✅ Storyboard complete!")
    print(f"   Scenes processed: {len(storyboard.scenes)}")

    total_queries = sum(len(s.search_queries) for s in storyboard.scenes)
    failed_queries = sum(1 for s in storyboard.scenes for q in s.search_queries if q.error)
    print(f"   Search queries: {total_queries} ({failed_queries} failed)")

    total_assets = sum(len(q.video_assets) for s in storyboard.scenes for q in s.search_queries)
    reranked_assets = sum(
        [
            1
            for s in storyboard.scenes
            for q in s.search_queries
            for a in q.video_assets
            if a.reranked_score is not None
        ],
    )
    print(f"   Video assets: {total_assets} ({reranked_assets} reranked)")

    return storyboard


# endregion
# endregion


# region COMPARISON: Sequential version for timing comparison
async def process_storyboard_sequential(description: str) -> Storyboard:
    """Sequential version - for comparison only."""
    print(f"🐌 Starting sequential processing: {description}\n")
    storyboard = Storyboard(description=description)

    storyboard.scenes = await generate_scenes_dspy(description)

    for scene in storyboard.scenes:
        scene.search_queries = await generate_search_queries_dspy(scene)

        for query in scene.search_queries:
            try:
                assets = await search_api_call(query)
                for asset in assets:
                    await rerank_dspy(asset, query)
                query.video_assets = assets
            except Exception as e:
                query.error = str(e)

    return storyboard


# endregion


# region Main execution
async def main():
    description = "A hero's journey through mystical lands"

    print("=" * 60)
    print("PARALLEL PROCESSING")
    print("=" * 60)
    start = asyncio.get_event_loop().time()
    storyboard_parallel = await process_storyboard(description)
    parallel_time = asyncio.get_event_loop().time() - start

    print("\n" + "=" * 60)
    print("SEQUENTIAL PROCESSING (for comparison)")
    print("=" * 60)
    start = asyncio.get_event_loop().time()
    storyboard_sequential = await process_storyboard_sequential(description)
    sequential_time = asyncio.get_event_loop().time() - start

    print("\n" + "=" * 60)
    print("PERFORMANCE COMPARISON")
    print("=" * 60)
    print(f"Parallel time:   {parallel_time:.2f}s")
    print(f"Sequential time: {sequential_time:.2f}s")
    print(f"Speedup:         {sequential_time / parallel_time:.1f}x faster")

    # Show a sample scene with its data
    if storyboard_parallel.scenes:
        sample_scene = storyboard_parallel.scenes[0]
        print(f"\n📋 Sample Scene #{sample_scene.scene_id}:")
        print(f"   Content: {sample_scene.content}")
        print(f"   Queries: {len(sample_scene.search_queries)}")
        if sample_scene.search_queries:
            sample_query = sample_scene.search_queries[0]
            print(f"   Sample query: {sample_query.query_text}")
            print(f"   Assets found: {len(sample_query.video_assets)}")


# endregion


if __name__ == "__main__":
    asyncio.run(main())
