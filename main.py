from flask import Flask, render_template, request, flash

# Use 'template' (singular) because you asked for template/index.html
app = Flask(__name__, template_folder='template')
app.secret_key = "change-this-in-prod"  # Needed for flash messages

# ---- Conversion tables ----
# We'll convert via base units: m (length), kg (mass), L (volume).
LENGTH_TO_M = {
    "m": 1.0,
    "km": 1000.0,
    "cm": 0.01,
    "mm": 0.001,
    "mi": 1609.344,
    "yd": 0.9144,
    "ft": 0.3048,
    "in": 0.0254,
}

MASS_TO_KG = {
    "kg": 1.0,
    "g": 0.001,
    "mg": 1e-6,
    "lb": 0.45359237,
    "oz": 0.028349523125,
    "tonne": 1000.0,  # metric
}

VOLUME_TO_L = {
    "L": 1.0,
    "mL": 0.001,
    "cup": 0.2365882365,  # US cup
    "pt": 0.473176473,     # US pint
    "qt": 0.946352946,     # US quart
    "gal": 3.785411784,    # US gallon
}

# Temperature needs special handling (not linear scale through zero)
TEMP_UNITS = ["C", "F", "K"]

CATEGORY_UNITS = {
    "length": sorted(LENGTH_TO_M.keys()),
    "mass":   sorted(MASS_TO_KG.keys()),
    "volume": sorted(VOLUME_TO_L.keys()),
    "temp":   TEMP_UNITS,
}


def convert_length(value, from_u, to_u):
    meters = value * LENGTH_TO_M[from_u]
    return meters / LENGTH_TO_M[to_u]


def convert_mass(value, from_u, to_u):
    kg = value * MASS_TO_KG[from_u]
    return kg / MASS_TO_KG[to_u]


def convert_volume(value, from_u, to_u):
    liters = value * VOLUME_TO_L[from_u]
    return liters / VOLUME_TO_L[to_u]


def convert_temp(value, from_u, to_u):
    # Convert from 'from_u' to Celsius
    if from_u == "C":
        c = value
    elif from_u == "F":
        c = (value - 32.0) * 5.0 / 9.0
    elif from_u == "K":
        c = value - 273.15
    else:
        raise ValueError("Unsupported temperature unit")

    # Convert from Celsius to 'to_u'
    if to_u == "C":
        return c
    elif to_u == "F":
        return c * 9.0 / 5.0 + 32.0
    elif to_u == "K":
        return c + 273.15
    else:
        raise ValueError("Unsupported temperature unit")


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None

    # Defaults for the form
    category = request.form.get("category", "length")
    from_unit = request.form.get("from_unit", CATEGORY_UNITS[category][0])
    to_unit = request.form.get("to_unit", CATEGORY_UNITS[category][1 if len(CATEGORY_UNITS[category]) > 1 else 0])
    amount_str = request.form.get("amount", "")

    if request.method == "POST":
        try:
            if category not in CATEGORY_UNITS:
                raise ValueError("Unknown category.")
            if from_unit not in CATEGORY_UNITS[category] or to_unit not in CATEGORY_UNITS[category]:
                raise ValueError("Units don't match the selected category.")

            amount = float(amount_str)

            if category == "length":
                result = convert_length(amount, from_unit, to_unit)
            elif category == "mass":
                result = convert_mass(amount, from_unit, to_unit)
            elif category == "volume":
                result = convert_volume(amount, from_unit, to_unit)
            elif category == "temp":
                result = convert_temp(amount, from_unit, to_unit)
            else:
                raise ValueError("Unsupported category.")

        except ValueError as e:
            error = str(e)
            flash(error, "error")

    return render_template(
        "index.html",
        categories=list(CATEGORY_UNITS.keys()),
        units_by_category=CATEGORY_UNITS,
        selected_category=category,
        selected_from=from_unit,
        selected_to=to_unit,
        amount=amount_str,
        result=result,
    )


if __name__ == "__main__":
    # For local dev
    app.run(host="0.0.0.0", port=5000, debug=True)
