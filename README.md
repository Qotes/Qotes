# Qotes

## A note application based on Flask

- Qotes is a web application based on Flask and MongoDB.
- Qotes is designed to help you with your notes especially study notes.
- Qotes uses **cards** as records of notes, which take Markdown for default.
- The cards is like nodes in a tree structure with the auther as the root, which means every card will consist of several cards and so on.
- Both in full content mode or just the broad outline mode can the cards be viewed.

## TECHNOLOGY COLOPHON

- HTML5, Bootstrap, jQuery
- Nginx, Flask, MongoDB

***

## Flask & MongoDB

- **Flask** is an interesting framework. There are many ways to implement a function in flask. It's concise but fabulous. I started this project just for a try but it turned out to be impressive.
- I wanted to have a try so I chose  **MongoDB** which I have never used before. I picked `flask_mongoengine` as the ODM at first. It was supposed to work like `flask_sqlalchemy` but it just let me down. And since I'm learning, why not use the `pymongo` directly? It worked, the docs of `pymongo` was a spectacular to me.

## Markdown

- The cards use **Markdown** as default text language.
- The cards will automatically use the `# [title]` as the title of a card and a list of `## [outline]` as a gist. These things will frame the the preview of the card.
- I designed this application to help me learn Python at first, so Qotes is basically supposed to display codes in a friendly way.
- There are many interesting things about markdown in this site except GFM. Maybe I will work on it after some of the more important utilities are implemented.

## User Interface

- I'm quite not good at Javescript or AngularJS and React or any other kind of these staffs. It took me a whole afternoon to learn JS and jQuery and implement the function of attaching cards to another by drawing and dropping. It turned out that JS is easy to learn but difficult to use.
- So I imported several open source JS scripts, most of which need improvement. I'm working on it.
- Basic functions are completed, such as posting a card in a single column swiftly or writing a card patiently with a powerful editor, single card bookmark during the session and the coming powerful searching bar.
- I'm thinking of changing all the front-end to Vue.js or React instead of Jinja2 and jQuery after API is completed.

## Thanks to them

- GLYPHICONS -- [http://glyphicons.com/](http://glyphicons.com/)
- Readable -- Thomas Park -- thomas@bootswatch.com
- Masonary -- [https://masonry.desandro.com/](https://masonry.desandro.com/)
- simplemde -- [https://github.com/sparksuite/simplemde-markdown-editor](https://github.com/sparksuite/simplemde-markdown-editor)
- MarkdownIME -- [https://github.com/laobubu/MarkdownIME](https://github.com/laobubu/MarkdownIME)
- to-markdown -- [https://github.com/domchristie/to-markdown](https://github.com/domchristie/to-markdown)
- moment.js -- [http://momentjs.com/](http://momentjs.com/)
- *Flask Web Development:Developing Web Applications with Python* -- Miguel Grinberg -- [https://github.com/miguelgrinberg](https://github.com/miguelgrinberg)
- *Stunning CSS3...A PROJECT-BASED GUIDE TO THE LATEST IN CSS* -- Zoe Mickley Gillenwater -- [http://zomigi.com/](http://zomigi.com/)

And developers of modules imported in the source code.

## TODO & WORKING ON

- RESTful API
- Ajax
- Search
- Pravite Cards
- Quote Cards
- More front-end things

***

## LICENSE & Other things

This version of Qotes is under *The MIT License (MIT)* which means you are free to do almost everything with the code of this project.

You can also visit the site by hand to get a preview of the project. Link: [http://qotes.top](http://qotes.top). The site blocked some functions because of local legal specifications. But all functions are designed to be available for any user. You can change a few configs to activate them(e.g. view&quote others' cards).

你可以访问[http://qotes.top](http://qotes.top)实际体验一下这个项目。因为某些规定的原因，本网站不支持查看或者引用他人的卡片。但是为了练习，这些功能都在程序设计时考虑到了并且实现了，只不过在实际运行中被故意封锁住了。你可以自己尝试更改设置来开放这些功能用作试验。

## Contact ME-<somarl@live.com>

The TODO is for me so it is in Chinese. Don't worry, the comments in the source code are all in English. If you want to contact me for more information or something else, please email to:
<somarl@live.com>