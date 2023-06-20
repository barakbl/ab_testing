from application import crud, models
from fastapi import HTTPException
import logging


def pick_variant(
    db, experiment: models.Experiment, variants: models.Variant, device_id: str
) -> (models.Variant, bool):
    """

    :param db: a db connection
    :param experiment:  experiment orm object
    :param variants: variants orm object
    :param device_id: the customer device id

    :return: a tuple of: selected variant object,
                         bool value that true if this is first access of deviceID
    """
    if not variants:
        logging.exception(f"not varients in db for expermient: {experiment.name}")
        raise HTTPException(status_code=500, detail="internal server error")

    # device already in db for specific experiment?
    device_view = crud.get_device_view(db, device_id, experiment)
    if device_view:
        return [v for v in variants if v["id"] == device_view.variant_id][0], False

    # if any variant has zero view, we want to at least view it once
    # this is against the main logic,  we can commented next 3 lines it if its not desirable
    zero_view = [v for v in variants if v["views"] == 0]
    if len(zero_view):
        return zero_view[0], True

    ## calculate scores - we will pick the lowest score -> the one that far away from dest by ratio
    picked_variant = None
    for variant in variants:
        variant["score"] = variant["views_percentage"] - variant["percentage"]
        if picked_variant is None or variant["score"] < picked_variant["score"]:
            picked_variant = variant

    if not picked_variant:
        return variants[0], True
    return picked_variant, True


def get_experiment(db, experiment_name: str, deviceID: str) -> dict:
    """

    :param db: db session
    :param experiment_name: experiment name to fetch
    :param deviceID: the customer deviceID
    :return: dict with variant id and name
    """
    logging.debug(
        f"get experiment for: experiment name: {experiment_name}  device: {deviceID}"
    )
    experiment = crud.get_experiment_by_name(db, experiment_name)
    if not experiment:
        logging.warning(f"access to expermient {experiment_name} which is not in db")
        raise HTTPException(status_code=404, detail="Item not found")
    variants = [e.__dict__ for e in experiment.variants]
    variant_sum = sum([e["ratio"] for e in variants])
    views = crud.get_views_count_by_experiment(db, experiment)

    # black formatted the next long line of code, this is for showcase, in practice it might not be a bad idea to split
    # normalized ratio to percentage from total
    variants = [
        dict(
            item,
            **{
                "percentage": item["ratio"] / variant_sum * 100,
                "views": views["variants"].get(item["id"], 0),
                "views_percentage": views["variants"].get(item["id"], 0)
                / views["total"]
                * 100
                if views["total"]
                else 0,
            },
        )
        for item in variants
    ]
    variant, is_new_device_view = pick_variant(db, experiment, variants, deviceID)
    if is_new_device_view:
        crud.create_view(db, variant["id"], deviceID)
    return {"variant_id": variant["id"], "variant_name": variant["name"]}
