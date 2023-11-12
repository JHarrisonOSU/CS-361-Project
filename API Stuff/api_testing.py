import requests


def get_medication_description(med_name):
    base_url = "https://api.fda.gov/drug/label.json"
    query = f"?search=generic_name:{med_name}&limit=1"
    response = requests.get(base_url + query)

    if response.status_code == 200:
        data = response.json()
        results = data.get("results", [])

        if results:
            description = results[0].get("description", ["No description available"])[0]
            return description
        else:
            return "No results found"
    else:
        return f"Error: {response.status_code}"


description = get_medication_description("LOSARTAN POTASSIUM AND HYDROCHLOROTHIAZIDE")
print("\n", description)
