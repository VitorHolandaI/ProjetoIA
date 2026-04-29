from dataclasses import dataclass, field

from .maze import Position


@dataclass
class KnowledgeBase:
    path_traffic: dict[Position, int] = field(default_factory=dict)
    entrance_counts: dict[Position, int] = field(default_factory=dict)
    landmark_seen_counts: dict[str, int] = field(default_factory=dict)
    landmark_escape_counts: dict[str, int] = field(default_factory=dict)
    landmark_capture_counts: dict[str, int] = field(default_factory=dict)

    def record_human_run(
        self,
        entrance: Position,
        path: list[Position],
        seen_landmarks: set[str],
        outcome: str,
    ) -> None:
        self.entrance_counts[entrance] = self.entrance_counts.get(entrance, 0) + 1
        for position in path:
            self.path_traffic[position] = self.path_traffic.get(position, 0) + 1
        for landmark_id in seen_landmarks:
            self._record_landmark(landmark_id, outcome)

    def traffic_score(self, position: Position) -> float:
        return min(1.0, self.path_traffic.get(position, 0) / 30.0)

    def landmark_safety(self, landmark_id: str) -> float:
        escape_count = self.landmark_escape_counts.get(landmark_id, 0)
        capture_count = self.landmark_capture_counts.get(landmark_id, 0)
        total = self.landmark_seen_counts.get(landmark_id, 0) + 1
        return (escape_count - capture_count) / total

    def landmark_danger(self, landmark_id: str) -> float:
        capture_count = self.landmark_capture_counts.get(landmark_id, 0)
        total = self.landmark_seen_counts.get(landmark_id, 0) + 1
        return capture_count / total

    def landmark_traffic(self, landmark_id: str) -> float:
        return min(1.0, self.landmark_seen_counts.get(landmark_id, 0) / 20.0)

    def entrance_activity(self, entrance: Position) -> float:
        return min(1.0, self.entrance_counts.get(entrance, 0) / 20.0)

    def _record_landmark(self, landmark_id: str, outcome: str) -> None:
        self.landmark_seen_counts[landmark_id] = self.landmark_seen_counts.get(landmark_id, 0) + 1
        if outcome == "escaped":
            counts = self.landmark_escape_counts
        elif outcome == "caught":
            counts = self.landmark_capture_counts
        else:
            return
        counts[landmark_id] = counts.get(landmark_id, 0) + 1

