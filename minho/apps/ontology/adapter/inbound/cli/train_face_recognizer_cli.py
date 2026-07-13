from __future__ import annotations

from ontology.app.dtos.face_training_dto import TrainFaceRecognizerCommand
from ontology.dependencies.face_training_provider import get_face_training_use_case


def main() -> None:
    use_case = get_face_training_use_case()
    result = use_case.train(
        TrainFaceRecognizerCommand(epochs=50, batch_size=16, image_size=224)
    )
    print(f"ok={result.ok} epochs={result.epochs} weights_path={result.weights_path}")


if __name__ == "__main__":
    main()
