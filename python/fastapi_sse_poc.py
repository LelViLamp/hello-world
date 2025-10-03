import asyncio
import random
from contextlib import asynccontextmanager
from datetime import datetime
from enum import Enum
from typing import Any, AsyncIterator, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from starlette.responses import StreamingResponse

# region config
MIN_WAIT_TIME = 1.0
MAX_WAIT_TIME = 5.0


# endregion

# region define events
class EventType(str, Enum):
    STORYBOARD_GENERATION_STARTED = "storyboard_generation_started"

    STORYBOARD_ANALYSIS_STARTED = "storyboard_analysis_started"
    STORYBOARD_ANALYSIS_COMPLETED = "storyboard_analysis_completed"

    SCENE_IDEA_GENERATION_STARTED = "scene_idea_generation_started"
    SCENE_IDEA_GENERATION_COMPLETED = "scene_idea_generation_completed"

    ALL_SCENE_TEXT_GENERATION_STARTED = "all_scene_text_generation_started"
    SINGLE_SCENE_TEXT_GENERATION_STARTED = "single_scene_text_generation_started"
    SINGLE_SCENE_TEXT_GENERATION_COMPLETED = "single_scene_text_generation_completed"
    ALL_SCENE_TEXT_GENERATION_COMPLETED = "all_scene_text_generation_completed"

    ALL_SCENES_ALL_QUERY_GENERATION_AND_EXECUTION_STARTED = "all_scenes_all_query_generation_and_execution_started"
    SINGLE_SCENE_ALL_QUERY_GENERATION_AND_EXECUTION_STARTED = "single_scene_all_query_generation_and_execution_started"

    SINGLE_SCENE_QUERY_GENERATION_STARTED = "single_scene_query_generation_started"
    SINGLE_SCENE_QUERY_GENERATION_COMPLETED = "single_scene_query_generation_completed"

    SINGLE_SCENE_ALL_QUERY_EXECUTION_STARTED = "single_scene_all_query_execution_started"
    SINGLE_SCENE_SINGLE_QUERY_EXECUTION_STARTED = "single_scene_single_query_execution_started"
    SINGLE_SCENE_SINGLE_QUERY_EXECUTION_COMPLETED = "single_scene_single_query_execution_completed"
    SINGLE_SCENE_ALL_QUERY_EXECUTION_COMPLETED = "single_scene_all_query_execution_completed"

    SINGLE_SCENE_ALL_QUERY_GENERATION_AND_EXECUTION_COMPLETED = "single_scene_all_query_generation_and_execution_completed"
    ALL_SCENES_ALL_QUERY_GENERATION_AND_EXECUTION_COMPLETED = "all_scenes_all_query_generation_and_execution_completed"

    STORYBOARD_GENERATION_COMPLETED = "storyboard_generation_completed"


class ProgressEvent(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    event_id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    data: Optional[dict[str, Any]] = None

    def to_sse(self) -> str:
        return f"data: {self.model_dump()}\n\n"


class EventEmitter:
    """Handles async event emission with queuing support for parallel operations"""

    def __init__(self):
        self._queue: asyncio.Queue[Optional[ProgressEvent]] = asyncio.Queue()
        self._closed = False

    async def emit(self, event: ProgressEvent) -> None:
        """Emit an event to the queue"""
        if self._closed:
            raise RuntimeError("Cannot emit events after emitter is closed")
        await self._queue.put(event)

    async def close(self) -> None:
        """Signal that no more events will be emitted"""
        self._closed = True
        await self._queue.put(None)  # Sentinel value

    async def events(self) -> AsyncIterator[ProgressEvent]:
        """Async iterator over emitted events"""
        while True:
            event = await self._queue.get()
            if event is None:  # Sentinel value indicating completion
                break
            yield event


# endregion

# region business logic
# region data models
class StoryboardAnalysis(BaseModel):
    _original_user_prompt: str

    title: str
    summary: str
    key_themes: list[str]
    people: list[str]
    locations: list[str]


class Scene(BaseModel):
    _original_scene_idea: str
    scene_id: UUID = Field(default_factory=uuid4)
    scene_index: int

    title: str
    content: str

    queries: Optional[list['Query']] = None


class Query(BaseModel):
    query_id: UUID = Field(default_factory=uuid4)
    query_index: int

    keywords: Optional[list[str]] = None
    locations: Optional[list[str]] = None
    people: Optional[list[str]] = None

    assets: Optional[list['Asset']] = None


class Asset(BaseModel):
    asset_id: UUID = Field(default_factory=uuid4)

    title: Optional[str] = None
    description: Optional[str] = None
    duration_in_seconds: Optional[float] = None

    video_url: str
    thumbnail_url: Optional[str] = None


class Storyboard(BaseModel):
    _original_storyboard_idea: str
    _storyboard_analysis: StoryboardAnalysis
    _scene_ideas: list[str]
    storyboard_id: UUID = Field(default_factory=uuid4)
    scenes: list[Scene]


# endregion

# region functions
# region helper
def generate_random_waiting_time(min_seconds: float = MIN_WAIT_TIME, max_seconds: float = MAX_WAIT_TIME) -> float:
    min_seconds = max(min_seconds, 0)
    max_seconds = max(max_seconds, 0)
    if max_seconds < min_seconds:
        raise ValueError("max_seconds must be greater than or equal to min_seconds")

    scaling_factor = random.random()
    return min_seconds + scaling_factor * (max_seconds - min_seconds)


# endregion

# region intermediate steps
async def analyse_storyboard(storyboard_idea: str) -> StoryboardAnalysis:
    await asyncio.sleep(generate_random_waiting_time())
    return StoryboardAnalysis(
        _original_user_prompt=storyboard_idea,
        title="A story about a hero's journey through mystical lands",
        summary="A story about a hero's journey through mystical lands",
        key_themes=["magic", "fantasy", "adventure"],
        people=["Daniel", "Prompto", "Kiba"],
        locations=["Salzburg", "Vienna", "Rome", "Phuket"],
    )


async def generate_scene_ideas(analysis: StoryboardAnalysis) -> list[str]:
    await asyncio.sleep(generate_random_waiting_time())
    return [
        "The Call to Adventure - Salzburg: Daniel discovers an ancient magical artefact in the misty mountains surrounding Salzburg. The artefact glows with ethereal light, revealing a cryptic map pointing towards Vienna.",
        "Meeting the Companion - Vienna: In Vienna's imperial palace gardens, Daniel encounters Prompto, a skilled mage who's been tracking the same magical phenomena. They forge an alliance as mysterious dark forces begin to stir.",
        "The Oracle's Warning - Rome: The duo travels to Rome where they meet Kiba, a warrior-sage guarding ancient ruins. Kiba reveals a prophecy about a gathering darkness and reluctantly joins their quest, warning them of trials ahead.",
        "The Trial of Elements - Journey to Phuket: During their voyage to Phuket, the trio faces their first major challenge—a storm conjured by dark magic. They must combine their unique abilities to survive, solidifying their bond.",
        "The Mystical Threshold - Phuket: On Phuket's shores, beneath a full moon, they discover a hidden temple entrance. Ancient guardians materialise, testing whether the heroes are worthy to enter the mystical realm beyond and confront the source of the darkness.",
    ]


async def generate_single_scene(scene_index: int, scene_idea: str) -> Scene:
    await asyncio.sleep(generate_random_waiting_time())
    return Scene(
        _original_scene_idea=scene_idea,
        scene_index=scene_index,
        title=f"Scene {scene_index}",
        content=f"Some yet-to-be-generated text",
    )


async def generate_single_scene_with_events(scene_index: int, scene_idea: str, emitter: EventEmitter) -> Scene:
    """Generate a single scene and emit events to the queue."""
    await emitter.emit(ProgressEvent(event_type=EventType.SINGLE_SCENE_TEXT_GENERATION_STARTED))

    scene = await generate_single_scene(scene_index, scene_idea)

    await emitter.emit(
        ProgressEvent(
            event_type=EventType.SINGLE_SCENE_TEXT_GENERATION_COMPLETED,
            data={"scene_index": scene_index, "scene_id": str(scene.scene_id)},
        ),
    )

    return scene


async def generate_queries_for_scene(scene: Scene) -> list[Query]:
    await asyncio.sleep(generate_random_waiting_time())
    queries = []
    for i in range(random.randint(0, 10)):
        query = Query(
            query_index=i,
            keywords=[f"keyword#{j}" for j in range(0, 4)],
        )
        queries.append(query)
    return queries


async def execute_single_query(query: Query) -> list[Asset]:
    await asyncio.sleep(generate_random_waiting_time())
    assets = []
    for i in range(random.randint(0, 10)):
        asset = Asset(
            title=f"Video #{i}",
            description=f"Video #{i} description",
            duration_in_seconds=random.random() * 10.0,
            video_url=f"https://example.com/video_{i}.mp4",
            thumbnail_url=f"https://example.com/video_{i}_thumbnail.jpg",
        )
        assets.append(asset)
    return assets


async def execute_query_with_events(query: Query, emitter: EventEmitter, scene_index: int) -> list[Asset]:
    """Execute a single query and emit events to the queue."""
    await emitter.emit(ProgressEvent(event_type=EventType.SINGLE_SCENE_SINGLE_QUERY_EXECUTION_STARTED))

    assets = await execute_single_query(query)

    await emitter.emit(
        ProgressEvent(
            event_type=EventType.SINGLE_SCENE_SINGLE_QUERY_EXECUTION_COMPLETED,
            data={
                "scene_index": scene_index,
                "query_index": query.query_index,
                "num_results": len(assets),
            },
        ),
    )
    return assets


async def generate_and_execute_queries_with_events(scene: Scene, emitter: EventEmitter) -> Scene:
    """Generate and execute all queries for a scene, emitting events."""
    await emitter.emit(ProgressEvent(event_type=EventType.SINGLE_SCENE_ALL_QUERY_GENERATION_AND_EXECUTION_STARTED))

    # step 1: generate queries
    await emitter.emit(ProgressEvent(event_type=EventType.SINGLE_SCENE_QUERY_GENERATION_STARTED))
    queries = generate_queries_for_scene(scene)
    scene.queries = await queries
    await emitter.emit(
        ProgressEvent(
            event_type=EventType.SINGLE_SCENE_QUERY_GENERATION_COMPLETED,
            data={"scene_index": scene.scene_index, "num_queries": len(scene.queries)},
        ),
    )

    # step 2: execute all queries for this scene in parallel
    await emitter.emit(ProgressEvent(event_type=EventType.SINGLE_SCENE_ALL_QUERY_EXECUTION_STARTED))
    query_tasks = [
        execute_query_with_events(query, emitter, scene.scene_index)
        for query in scene.queries
    ]
    all_query_results = await asyncio.gather(*query_tasks)

    for query, assets in zip(scene.queries, all_query_results):
        query.assets = assets
    await emitter.emit(
        ProgressEvent(
            event_type=EventType.SINGLE_SCENE_ALL_QUERY_EXECUTION_COMPLETED,
            data={
                "scene_index": scene.scene_index,
                "num_queries": len(scene.queries),
                "num_results": sum(len(q.assets) for q in scene.queries),
            },
        ),
    )
    await emitter.emit(
        ProgressEvent(
            event_type=EventType.SINGLE_SCENE_ALL_QUERY_GENERATION_AND_EXECUTION_COMPLETED,
            data={
                "scene_index": scene.scene_index,
                "num_queries": len(scene.queries),
                "num_results": sum(len(q.assets) for q in scene.queries),
            },
        ),
    )

    return scene


# endregion


# region put it all together
async def generate_storyboard_with_events(storyboard_idea: str, emitter: EventEmitter) -> Storyboard:
    await emitter.emit(
        ProgressEvent(event_type=EventType.STORYBOARD_GENERATION_STARTED),
    )

    # step 1: analyse storyboard
    await emitter.emit(ProgressEvent(event_type=EventType.STORYBOARD_ANALYSIS_STARTED))
    analysis = await analyse_storyboard(storyboard_idea)
    await emitter.emit(
        ProgressEvent(
            event_type=EventType.STORYBOARD_ANALYSIS_COMPLETED,
            data=analysis.model_dump(),
        ),
    )

    # step 2: generate scene ideas
    await emitter.emit(ProgressEvent(event_type=EventType.SCENE_IDEA_GENERATION_STARTED))
    scene_ideas = await generate_scene_ideas(analysis)
    await emitter.emit(
        ProgressEvent(
            event_type=EventType.SCENE_IDEA_GENERATION_COMPLETED,
            data={"num_scene_ideas": len(scene_ideas)},
        ),
    )

    # step 3: generate texts for each scene in parallel
    await emitter.emit(ProgressEvent(event_type=EventType.ALL_SCENE_TEXT_GENERATION_STARTED))
    scene_tasks = [
        generate_single_scene_with_events(scene_index, scene_idea, emitter)
        for scene_index, scene_idea in enumerate(scene_ideas)
    ]
    scenes = await asyncio.gather(*scene_tasks)
    sorted(scenes, key=lambda s: s.scene_index)
    await emitter.emit(
        ProgressEvent(
            event_type=EventType.ALL_SCENE_TEXT_GENERATION_COMPLETED,
            data={"num_scenes": len(scenes)},
        ),
    )

    # step 4: generate and execute queries in parallel for all scenes
    await emitter.emit(
        ProgressEvent(event_type=EventType.ALL_SCENES_ALL_QUERY_GENERATION_AND_EXECUTION_STARTED),
    )
    query_processing_tasks = [
        generate_and_execute_queries_with_events(scene, emitter)
        for scene in scenes
    ]
    scenes = await asyncio.gather(*query_processing_tasks)
    await emitter.emit(
        ProgressEvent(
            event_type=EventType.ALL_SCENES_ALL_QUERY_GENERATION_AND_EXECUTION_COMPLETED,
            data={
                "num_scenes": len(scenes),
                "num_queries": sum(len(s.queries) for s in scenes),
                "num_results": sum(len(q.assets) for s in scenes for q in s.queries),
            },
        ),
    )

    # assemble everything into an object and emit final event
    storyboard = Storyboard(
        _original_storyboard_idea=storyboard_idea,
        _storyboard_analysis=analysis,
        _scene_ideas=scene_ideas,
        scenes=scenes,
    )
    await emitter.emit(
        ProgressEvent(
            event_type=EventType.STORYBOARD_GENERATION_COMPLETED,
            data={"storyboard_id": str(storyboard.storyboard_id)},
        ),
    )
    return storyboard


# endregion
# endregion
# endregion


# region simulate event emission and consumption (by printing to console)
async def print_event_to_console(event):
    print(f"{event.timestamp} [{event.event_type.value}]", end="")
    if event.data:
        print(f": {event.data}", end="")
    print()


async def simulate_storyboard_generation(storyboard_idea: str) -> Storyboard:
    emitter = EventEmitter()
    storyboard_task = asyncio.create_task(
        generate_storyboard_with_events(storyboard_idea, emitter),
    )

    async def close_after_completion():
        await storyboard_task
        await emitter.close()

    asyncio.create_task(close_after_completion())

    async for event in emitter.events():
        await print_event_to_console(event)

    storyboard = await storyboard_task
    return storyboard


# endregion


# region FastAPI PoC
class StoryboardRequest(BaseModel):
    storyboard_idea: str
    stream: bool = True


class StoryboardResponse(BaseModel):
    storyboard: Storyboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting FastAPI app")
    yield
    print("Stopping FastAPI app")


app = FastAPI(lifespan=lifespan)


async def event_stream(storyboard_idea: str):
    emitter = EventEmitter()
    storyboard_task = asyncio.create_task(
        generate_storyboard_with_events(storyboard_idea, emitter),
    )

    async def close_after_completion():
        try:
            await storyboard_task
        finally:
            await emitter.close()

    asyncio.create_task(close_after_completion())

    async for event in emitter.events():
        # Format as SSE
        yield f"event: progress\ndata: {event.model_dump()}\n\n"

    storyboard = await storyboard_task
    yield f"event: complete\ndata: {storyboard.model_dump()}\n\n"


@app.post("/api/storyboards/generate", response_model=StoryboardResponse)
async def generate_storyboard_endpoint(request: StoryboardRequest):
    if not request.storyboard_idea.strip():
        raise HTTPException(status_code=400, detail="Storyboard idea cannot be empty")

    if request.stream:
        return StreamingResponse(
            event_stream(request.storyboard_idea),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )
    else:
        emitter = EventEmitter()
        storyboard_task = asyncio.create_task(
            generate_storyboard_with_events(request.storyboard_idea, emitter),
        )

        async def close_after_completion():
            await storyboard_task
            await emitter.close()

        asyncio.create_task(close_after_completion())

        async for _ in emitter.events():
            pass

        storyboard = await storyboard_task
        return StoryboardResponse(storyboard=storyboard)


# endregion


if __name__ == '__main__':
    storyboard = asyncio.run(
        simulate_storyboard_generation("A story about a hero's journey through mystical lands"),
    )
    print("", "-" * 42 * 2, storyboard, sep="\n")
