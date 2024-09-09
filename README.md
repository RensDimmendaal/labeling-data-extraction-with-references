# Fasthtml instructor labeling

*This is not a finished product, but a proof of concept*

So far this is just some hacking around for to see if I can make a simple labeling tool for the case of data extraction with citations. Main things I'm interested in:

1. Updating the citations by selecting text in the source text
2. Reviewing the total dataset and getting a general sense of the quality of the predictions
    - metrics
    - some indications where data might be of low quality

## Demo video

https://github.com/user-attachments/assets/03a57aeb-926d-468a-8205-be62f7813635

## Run

Run the app.py 

If using uv

```
uv run app.py
```

## TODO

- [ ] Save human labels as something different than the original generated labels
- [ ] Show human label / LLM agreement / LLM disagreemment in the table with color
- [ ] Add some kind of "peek" feature to see the predictions / human labels when hovering over a value
- [ ] Let click on value lead to labeling ui where you can adjust the prediction immediately
- [ ] Allow quotes to be longer than one line
- [ ] Add login to save different users' labels
- [ ] Add a header to switch back to the table overview...
- [ ] Allow multiple datasets (e.g. each with their own definiition, and predictions, and labels)
