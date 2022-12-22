# FSND Final Project

## Snack App

Snack App is used to display various kinds of snacks by categories, as with comments from consumers. The application function includes:
1. Display snacks. A snack (or item) should have its' brand, category and comment from consumers
2. Update snacks
3. Delete snacks

## APIs
GET `'/categories'`
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains an object of id: category_string key: value pairs.
- Example:
```bash
{
    "1": "Chips",
    "2": "Cookies",
    "3": "Dried Fruits",
    "4": "Popcorn",
    "5": "Pretzels"
}
```

GET `'/items'`
- Fetches all items in database with id as key
- Request Arguments: None
- Returns: A list of items with id, title, brand, category and comment
- Example:
```bash
"items": [
        {
            "brand": "belVita",
            "category": 2,
            "comment": "Perfect for Breakfast on the Go",
            "id": 2,
            "title": "Cranberry Orange Breakfast Biscuits"
        }
]
```

DELETE `'/items/<int:item_id>'`
- Delete the item with the given item_id from database
- Request Arguments: `item_id`
- Returns: The deleted item with id, title, brand, category and comment
- Example:
```bash
"items": [
        {
            "brand": "belVita",
            "category": 2,
            "comment": "Perfect for Breakfast on the Go",
            "id": 2,
            "title": "Cranberry Orange Breakfast Biscuits"
        }
]
```

PATCH `'/items/<int:item_id>'`
- Update the item with the given item_id
- Request Arguments: `item_id`
- Returns: The updated item with id, title, brand, category and comment
- Example:
```bash
"items": [
        {
            "brand": "belVita",
            "category": 2,
            "comment": "Perfect for Breakfast on the Go",
            "id": 2,
            "title": "Cranberry Orange Breakfast Biscuits"
        }
]
```

## Roles
VISITOR
- Permissions: GET `'/categories'`, GET `'/items'`

ADMIN
- Permissions: GET `'/categories'`, GET `'/items'`, DELETE `'/items/<int:item_id>'`, PATCH `'/items/<int:item_id>'`

