new structure on Google Cloud:

- venues
  - venues/94th Aero Squadron Restaurant_
    - venues/94th Aero Squadron Restaurant_/94th Aero Squadron Restaurant_.pdf
    - venues/94th Aero Squadron Restaurant_/img001.jpg
    - venues/94th Aero Squadron Restaurant_/img002.jpg
    - venues/94th Aero Squadron Restaurant_/img003.jpg
    - venues/94th Aero Squadron Restaurant_/img004.jpg
    ...

  - venues/Ace Hotel Palm Springs
    - venues/Ace Hotel Palm Springs/Ace Hotel Palm Springs.pdf
    - venues/Ace Hotel Palm Springs/img001.jpg
    - venues/Ace Hotel Palm Springs/img002.jpg
    - venues/Ace Hotel Palm Springs/img003.jpg
    - venues/Ace Hotel Palm Springs/img004.jpg
    ...

  - venues/Aero Club of Southern California
    - venues/Aero Club of Southern California/Aero Club of Southern California.pdf
    - venues/Aero Club of Southern California/img001.jpg
    - venues/Aero Club of Southern California/img002.jpg
    - venues/Aero Club of Southern California/img003.jpg
    - venues/Aero Club of Southern California/img004.jpg
    ...

What is stored on GitHub repo?
- vectorstore
- streamlit app

When new pdf is added:

- trigger GitHub action:
  - use google cloud function to trigger github action
  - download pdf from cloud
  - extract images from pdf
  - upload images to cloud
  - extract text/tables/etc from pdf
  - store in vectorstore
  - push vectorstore to GitHub repo
    - Streamlit Cloud will reload app

What happens when a Streamlit app instance is created?

- Streamlit app will download images from cloud
- Streamlit app will load vectorstore into memory
- Streamlit app will run
