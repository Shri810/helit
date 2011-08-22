# Copyright 2011 Tom SF Haines

# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.



class ProbCat:
  """A standard interface for a probabilistic classifier. Provides an interface for a system where you add a bunch of 'samples' and their categories, and can then request the probability that new samples belong to each category. Designed so it can be used in an incrimental manor - if a classifier does not support that it is responsible for prentending that it does, by retrainning each time it is used after new data has been provided. Being probabilistic the interface forces the existance of a prior - it can be a fake-prior that is never used or updated, but it must exist. Obviously it being handled correctly is ideal. The 'sample' object often passed in is category specific, though in a lot of cases will be something that can be interpreted as a 1D numpy array, i.e. a feature vector. The 'cat' object often passed in represents a category - whilst it can be model specific it is generally considered to be a python object that is hashable and can be tested for equality. Being hashable is important to allow it to key a dictionary."""

  def priorAdd(self, sample):
    """Adds a sample to the prior; being that it is the prior no category is provided with. This can do nothing, but is typically used to build a prior over samples when the category is unknown."""
    raise NotImplementedError('priorAdd has not been implimented.')

  def add(self, sample, cat):
    """Given a sample and its category this updates the model, hopefully incrimentally during this method call, but otherwise when the model is next needed. Stuff added to a specific category should *not* be added to the prior by this method - a user can decide to do that by additionally calling priorAdd if they so choose."""
    raise NotImplementedError('add has not been implimented.')


  def getSampleTotal(self):
    """Returns the total number of samples that have been provided to train the classifier (Does not include the samples provided to build the prior.)."""
    raise NotImplementedError('add has not been implimented.')


  def getCatTotal(self):
    """Returns the total number of categories that have been provided to the classifier."""
    raise NotImplementedError('getCatTotal has not been implimented.')

  def getCatList(self):
    """Returns a list of all the categories that the classifier has examples of."""
    raise NotImplementedError('getCatList has not been implimented.')

  def getCatCounts(self):
    """Returns a dictionary indexable by each of the categories that goes to how many samples of that category have been provided. The returned dictionary must not be edited by the user."""
    raise NotImplementedError('getCatCounts has not been implimented.')


  def getDataProb(self, sample):
    """Returns a dictionary indexed by the various categories, with the probabilities of the sample being drawn from the respective categories. Must also include an entry indexed by 'None' that represents the probability of the sample comming from the prior. Note that this is P(data|category,model) - you probably want it reversed, which requires Bayes rule be applied."""
    raise NotImplementedError('getDataProb has not been implimented.')


  def getProb(self, sample, weight = False, conc = None):
    """This calls through to getDataProb and then applies Bayes rule to return a dictionary of values representing P(data,category|model) = P(data|category,model)*P(category). Note that whilst the two terms going into the return value will be normalised the actual return value will not - you will typically normalise to get P(category|data,model). The weight parameter indicates the source of P(class) - False (The default) indicates to use a uniform prior, True to weight by the number of instances of each category that have been provided to the classifier. Alternativly a dictionary indexed by the categories can be provided of weights, which will be normalised and used. By default the prior probability is ignored, but if a concentration (conc) value is provided it assumes a Dirichlet process, and you will have an entry in the return value, indexed by None, indicating the probability that it belongs to a previously unhandled category. For normalisation purposes conc is always assumed to be in ratio to the number of samples that have been provided to the classifier, regardless of weight."""
    # Get the data probabilities...
    dprob = self.getDataProb(sample)

    # Calculate the class probabilities, including normalisation and the inclusion of conc if need be...
    if weight==False: cprob = dict(map(lambda c: (c,1.0), self.getCatList()))
    elif weight==True: cprob = dict(self.getCatCounts())
    else: cprob = dict(weight)
    
    norm = float(sum(cprob.itervalues()))
    if conc!=None: # Adjust norm so it all sums to 1.
      conc = float(conc) / self.getSampleTotal()
      norm /= 1.0 - conc

    for cat in cprob.iterkeys(): cprob[cat] /= norm

    if conc!=None: cprob[None] = conc

    # Multiply it all out and return...
    ret = dict(cprob)
    for cat in ret.iterkeys():
      ret[cat] *= dprob[cat]
    return ret


  def getCat(self, sample, weight = False, conc = None):
    """Simply calls through to getProb and returns the category with the highest probability. If conc is provided it can be None, to indicate a new category is more likelly than any of the existing ones. A simple conveniance method."""
    prob = self.getProb(sample, weight, conc)
    
    best = None
    ret = None
    
    for cat, p in prob.iteritems():
      if best==None or p>best:
        best = p
        ret = cat

    return ret
