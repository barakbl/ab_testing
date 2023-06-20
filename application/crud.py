from sqlalchemy.orm import Session
from sqlalchemy import func

from application import models


def get_views_count_by_experiment(db: Session, experiment: models.Experiment) -> dict:
    vids = [v.id for v in experiment.variants]
    views = (
        db.query(models.VariantViews.variant_id, func.count(models.VariantViews.id))
        .filter(models.VariantViews.variant_id.in_(vids))
        .group_by(models.VariantViews.variant_id)
        .all()
    )
    return {
        "total": sum([v[1] for v in views]),
        "variants": {k[0]: k[1] for k in views},
    }


def get_experiment_by_name(
    db: Session, name: str, is_active: bool = True
) -> models.Experiment:
    experiments = (
        db.query(models.Experiment)
        .filter(models.Experiment.name == name, is_active == is_active)
        .first()
    )
    return experiments


def create_view(db: Session, variant_id: int, device_id: str) -> models.VariantViews:
    variant_view = models.VariantViews(variant_id=variant_id, device_id=device_id)
    db.add(variant_view)
    db.commit()
    return variant_view


def get_device_view(
    db: Session, device_id: str, experiment: models.Experiment
) -> models.VariantViews:
    """

    :param db:
    :param device_id: deviceID from client
    :param experiment: - experiment model
    :return:
    """

    # we might consider to add experiment_id as a col in views table for better performance
    vids = [v.id for v in experiment.variants]
    view = (
        db.query(models.VariantViews)
        .filter(
            models.VariantViews.variant_id.in_(vids),
            models.VariantViews.device_id == device_id,
        )
        .first()
    )
    return view
