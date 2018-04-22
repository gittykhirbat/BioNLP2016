#Given client's responses, recommeded top 10 questions that might be relevant
#Author: Gitansh Khirbat
#Date: 22 April 2018

####################################
#1. Read client's response data 
## ATM: Manually storing it

#Set up client's response class

class clientData:
    def __init__(self, clientId, businessName, websiteLink, websiteData, aboutUsLink, aboutUsData, industry,
                businessDesc, interestingFeatures, appealingFeatures, personDesc, discussionTopics, competitor, 
                usp, customerInfo, vision):
        self.clientId = clientId;
        self.businessName = businessName;
        self.websiteLink = websiteLink;
        self.websiteData = websiteData;
        self.aboutUsLink = aboutUsLink;
        self.aboutUsData = aboutUsData;
        self.industry = industry;
        self.businessDesc = businessDesc;
        self.interestingFeatures = interestingFeatures;
        self.appealingFeatures = appealingFeatures;
        self.personDesc = personDesc;
        self.discussionTopics = discussionTopics;
        self.competitor = competitor;
        self.usp = usp;
        self.customerInfo = customerInfo;
        self.vision = vision;
        
    def display(self):
        return [self.clientId, self.businessName, self.websiteLink, self.websiteData, self.aboutUsLink, 
        self.aboutUsData, self.industry, self.businessDesc, self.interestingFeatures, self.appealingFeautres,
        self.personDesc, self.discussionTopics, self.competitor, self.usp, self.customerInfo, self.vision]

#Set up question class

class questionData:
    def __init__(self, questionId, modifierType, modifier, suggestion):
        self.questionId = questionId
        self.modifierType = modifierType
        self.modifier = modifier
        self.suggestion = suggestion

    def display(self):
        return [self.questionId, self.modifierType, self.modifier, self.suggestion]


#2. Extract keyphrases from the textual responses

#3. Extract topics from the textual responses

#4. For each of the client's response topics, find out the questions, prepositions, comparisons, alphabeticals, related from answerthepublic.com

#5. Find the most relevant questions for the client

#6. Find the most relevant keywords/keyphrases for the client

