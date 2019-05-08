# \>>AnnoMathTeX<<

AnnoMathTeX is a LaTeX text and formula annotation recommendation tool for STEM (Science, Technology, Engineering, 
Mathematics) documents. It allows users to annotate 
identifiers in mathematical formulae, the entire formula as well as the named entities contained in a document 
(recommended formats being .tex or .txt) with the corresponding concept. Theses concepts are extracted from a number of 
different sources.

[Wikidata](https://www.wikidata.org) being one of them, in which case the selected token is annotated
with the [Wikidata QID](https://en.wikipedia.org/wiki/Wikidata#Items).

## Motivation
Machine Learning has proven time and time again to be extremely useful in classification tasks. However, very large 
amounts of labeled data are necessary to train machine learning methods. Currently, there is no large enough labeled 
dataset containing mathematical formulae annotated with their semantics available, that could be used to train machine 
learning models. >>AnnoMathTeX<< offers a first approach to facilitate the annotation of mathematical formulae in STEM 
documents, by recommending the concept associated to a certain identifier of formula to the user who is annotating the 
document.

The recommendations for the concepts are taken from four different sources:
 
## Features

What makes your project stand out? Include logo/demo screenshot etc.

## Components/Modules/Workflow

Visualize an overview of the different components/modules of the system as well as the workflow and describe the individual parts

## Very Short Code Examples

Show what the library does as **concisely** as possible, developers should be able to figure out **how** your project solves their problem by looking at the code example. Make sure the API you are showing off is obvious, and that your code is short and concise. See the [news-please project](https://github.com/fhamborg/news-please/blob/master/README.md#use-within-your-own-code-as-a-library) for example.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

What things you need to install the software and how to install them

Python version >=3.6 is recommended.
Django 


```
Give examples
```

### Installing

Clone or download the repository. In your shell navigate to the folder [AnnoMathTeX](/AnnoMathTeX) and create & activate
a new virtual environment. Then run the command
```
pip install -r requirements.txt
```



End with an example of getting some data out of the system or using it for a little demo

## API Reference

Depending on the size of the project, if it is small and simple enough the reference docs can be added to the README. For medium size to larger projects it is important to at least provide a link to where the API reference docs live.

## How to use? (maybe optional)

In a terminal navigate to the folder where the manage.py file sits ([AnnoMathTeX/annomathtex](/AnnoMathTeX/annomathtex))
and run the command
```python
python manage.py runserver
```
In your browser navigate to [http://127.0.0.1:8000/file_upload/](http://127.0.0.1:8000/file_upload/). Any browser should 
work, although we recommend using Google Chrome.

## Results

If you are about to complete your project, include your preliminary results that you also show in your final project presentation, e.g., precision/recall/F1 measure and/or figures highlighting what your project does with input data. If applicable, at first briefly describe the dataset your created/use and the use cases.

If you are about to complete your thesis, just include the most important findings (precision/recall/F1 measure) and refer the to the corresponding pages in your thesis document.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.md](LICENSE.md) file for details

## Built With

* [Django](https://www.djangoproject.com) - The web framework used

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/AnnoMathTeX/contributing) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* Ian Mackerracher
* Philipp Scharpf
See also the list of [contributors](https://github.com/philsMINT/AnnoMathTeX/contributors) who participated in this project.

## Acknowledgments

We thank...
