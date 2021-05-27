import requests, re, json
from simplified_scrapy import SimplifiedDoc

"""
Einsteinfessor's internal notes by wakils

We have two models.
Model 1 is present when the user requests the Calculation after having it completed.
Model 2 is present when the user requests the Calculation before having it completed.

What are the differences?
Model 1 delivers every piece of data we need, including extra.
Model 2 delivers the same as model 1, but with some exceptions.

Model 2 exceptions:
- No homework title is directly assigned in the object. This means we have to use
  an alternative way to retrieve the homework title. This method is not as stable
  as retrieving directly from the model, but atleast there are alternatives...
  The method involves receiving the homework title directly from the HTML code
  The title to be exact.
- Second observation is that this key is non existent:
  loadedJson['timeTillHomeworkElementSessionEnds']
  Which is quite odd and this requires further investigation.

Question exceptions:
Regardless of model 2 and 1 some questions might differentiate from others in the
way of structuring the object.
A question can either be a multiple choice question or not (as of what I have observed by now).
If multiple choice this key will exist (and the other won't): loadedJson['questions'][QN]['answers'].
If not this key will exist (and the other won't): loadedJson['questions'][QN]['Answer'].

The key 'Answer' doesn't provide an actual answer. This means we have to do something like
provide 'null' in the answer_options and 0 in correct_answer. Then make a check in every
application that uses the Einsteinfessor REST API. Quite unfortunate.
"""

def getResultsRaw(code):
    questions = []
    try:
        jsonObject = code[code.find('{"answerDelay"'):].split('};')[0] + '}' if code.find('{"homeworkElementSessionId":"') == -1 else code[code.find('{"homeworkElementSessionId":"'):].split(');')[0]
        loadedJson = json.loads(jsonObject)
        model = 1 if 'timeTillHomeworkElementSessionEnds' in loadedJson else 2
    except Exception as e:
        return {"status_code": 0, "message": 'Der var desværre en fejl ved at udregne svarene', "error": e}

    def cleanme(content):
        content = content.replace('<p>', '\n').replace('</mn><mn>', '/')
        cleaned = SimplifiedDoc(content).removeHtml(content).replace(
            "\\u00e5", "å").replace(
            "\\u00f8", "ø").replace(
            "\\u00e6", "æ").replace(
            "\\u00b7", "*").replace(
            '\\u00af\\u00af', '').replace(
            '\\u00af', '=').replace(
            '1 1', '').replace(
            '\\u2212', '-').replace(
            '&UnderBar; &UnderBar;', '').replace(
            '&UnderBar;', '=').replace(
            '\\u22c5', '*').replace(
            '\\u21d4', ' <-> ').replace(
            '\\u2062', '').replace(
            '&InvisibleTimes;', '').replace(
            '\\u00e9', 'é')
        return cleaned
        
    for QN, ques in enumerate(loadedJson['questions']):
        question_lesson_id = ques['Lesson']['id']
        question_lesson_title = ques['Lesson']['title']
        question_question = cleanme(ques['Question']['question'])

        #question_explanation
        if ques['Question']['explanation']:
            question_explanation = cleanme(ques['Question']['explanation'])
        else:
            question_explanation = 'Der kunne desværre ikke findes nogen forklaring til dette spørgsmål.'


        #question_answer_options
        to_be_added = []
        try:
            for option in ques['answers']:
                to_be_added.append(
                    cleanme(
                        option['Answer']['answer']
                    )
                )
            question_answer_options = {'index': QN, 'options': to_be_added}
        except:
            pass

        #question_correct
        if model == 1:
            if 'answers' in ques:
                for AO, elm in enumerate(ques['answers']):
                    if ques['answers'][AO]['Answer']['correct']:
                        question_correct = AO

        # Collect everything in a list
        quesDict = {
            'question': question_question,
            'lesson_title': question_lesson_title,
            'lesson_id': question_lesson_id,
            'explanation': question_explanation,
        }
        if model == 1:
            if 'question_correct' in locals():
                quesDict['correct'] = question_correct
        
        if 'question_answer_options' in locals():
            if question_answer_options['index'] == QN:
                quesDict['answer_options'] = question_answer_options['options']

        questions.append(quesDict)
    
    # Finally create the output object
    results = {
        'homework_title': cleanme(loadedJson['homeworkName']) if model == 1 else code[code.find('<span class="no-link">Lektie: ')+30:].split('</span>')[0],
        'question': questions
    }
    if model == 1:
        results['time_left'] = loadedJson['timeTillHomeworkElementSessionEnds']

    """

    GUIDE ON THE RESULTS DICTIONARY (RETURN VALUE):
    Disclaimer: The returned value is dumped to a string.

    QN = Question Number
    AO = Answer Option

    results['homework_title']
    results['time_left'] - MODEL 1 SPECIFIC
    results['question'][QN]['question']
    results['question'][QN]['lesson_title']
    results['question'][QN]['lesson_id']
    results['question'][QN]['explanation']
    results['question'][QN]['answer_options'] - Will NOT be included in every question. Make sure to check...
    results['question'][QN]['correct'] - MODEL 1 SPECIFIC

    """

    return json.dumps(results)


# Just for testing purposes
if __name__ == "__main__":
    import os
    f = open(os.path.dirname(os.path.realpath(__file__))+"\html.txt", "r")
    code = ''.join(f.readlines())
    f.close()

    getResultsRaw(code)