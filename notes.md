Backend
The backend GET /data endpoint was expanded in order to link citations and redact personal data.
Design choices included data consistency. The way I have coded the references enables references to be matched using IDs rather than being hardcoded and so not manually being hardcoded. Another choice was maintainability is also used as same processing functions can be reused for new data. Ensuring urls belong within hostname, then have a scheme as either http or https ensures unsuitable URLs from generating links. and using uv to run python scripts faester. I extended the existing /data endpoint in routers/data.py to process the source references before returning data to the frontend.
I used a dictionary to associate source IDs with their corresponding URLs, allowing references to be resolved efficiently without hardcoding individual links. I used Python's re.sub() to identify citation tags and replace them with HTML links.
I also used urlparse() to extract sections from URLs and validate these as well as construct the favicon.

Personal Data Redaction
Gliner2 uses the extraction method called Extract_entities, I configured the model to identify full names, first names, last names, email addresses and phone numbers. by using the extract_entities feature. we create the detections label and pii loables
I used include_spans=True to retrieve the start and end character positions of each detected entity, and passed these results to Presidio using RecognizerResult. Then looping through each of the model detection with the for loop we can then see if the entity is one that needs to be replaced. 
Then by appending each detection into a Presidio object such as results (namely from Code), and by using the replacement operators you can anonimize the entities.
Presidio's AnonymizerEngine then replaces the detected text with [NAME], [EMAIL] or [PHONE]. 
A design choice was maintainability, as I reused the GLiNER2 model loaded at application startup through FastAPI dependency injection, by using depends(get_model), which loads the model from dependencies.py to then inject the result into get_data, rather than loading a new model for every request.
Performing this processing in the backend means the frontend receives the redacted question instead of the original question.

Finally for the frontend, I maintained the component structure and a synchronous ContentList función that fetches the processed data from the FastAPI backend, mapping each returned record to an indivudal content component, displaying the redacted question and links, and kept tailwind.css as the format for a readable display.


Testing and Limitations
Implementation was succesful for all four data records, with data endpoints being fetched and displayed with redacted data, with favicons and the right link for their sources. Couple of issues did arise initially when importing misnamed data structures though this was then fixed, and port 8000 launched succesfully, then implementing the front end display, resulting in a functional website.

 