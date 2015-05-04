# Administration

## Adding users

See `admin_tools.add_newly_joined_user`

## Adding holidays

See `admin_tools/import_ical.py`

## Correcting inconsistencies caused by modifying vacations from past years

Run `models.UserYearlyArchive.regenerateArchive` for every year >= of the year where you introduced changes (and only for the user you introduced changes).
Note that **this will reset all data stored in the archive**. If the user has any custom data specific for that year, **information will be lost**!
