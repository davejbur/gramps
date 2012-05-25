#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

# $Id$

#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from xml.sax import handler
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# Gramps modules
#
#-------------------------------------------------------------------------
from gen.filters._genericfilter import GenericFilterFactory
from gen.filters import rules

#-------------------------------------------------------------------------
#
# FilterParser
#
#-------------------------------------------------------------------------
class FilterParser(handler.ContentHandler):
    """Parses the XML file and builds the list of filters"""
    
    def __init__(self, gfilter_list):
        handler.ContentHandler.__init__(self)
        self.gfilter_list = gfilter_list
        self.f = None
        self.r = None
        self.a = []
        self.cname = None
        self.namespace = 'Person'
        
    def setDocumentLocator(self, locator):
        self.locator = locator

    def startElement(self, tag, attrs):
        if tag == "object":
            if attrs.has_key('type'):
                self.namespace = attrs['type']
            else:
                self.namespace = "generic"
        elif tag == "filter":
            self.f = GenericFilterFactory(self.namespace)()
            self.f.set_name(attrs['name'])
            if attrs.has_key('function'):
                try:
                    if int(attrs['function']):
                        op = 'or'
                    else:
                        op = 'and'
                except ValueError:
                    op = attrs['function']
                self.f.set_logical_op(op)
            if attrs.has_key('invert'):
                self.f.set_invert(attrs['invert'])
            if attrs.has_key('comment'):
                self.f.set_comment(attrs['comment'])
            self.gfilter_list.add(self.namespace, self.f)
        elif tag == "rule":
            save_name = attrs['class']
            if save_name in old_names_2_class:
                self.r = old_names_2_class[save_name]
            else:
                try:
                    # First try to use fully qualified name
                    exec 'self.r = %s' % save_name
                except (ImportError, NameError, AttributeError ):
                    # Now try to use name from rules.namespace
                    mc_match = save_name.split('.')
                    last_name = mc_match[-1]
                    try:
                        exec 'self.r = rules.%s.%s' % (
                            self.namespace.lower(), last_name)
                    except (ImportError, NameError, AttributeError ):
                        print "ERROR: Filter rule '%s' in "\
                              "filter '%s' not found!"\
                                  % (save_name, self.f.get_name())
                        self.r = None
                        return
            self.a = []
        elif tag == "arg":
            self.a.append(attrs['value'])

    def endElement(self, tag):
        if tag == "rule" and self.r is not None:
            if len(self.r.labels) != len(self.a):
                self.__upgrade()
            if len(self.r.labels) < len(self.a):
                print _("WARNING: Too many arguments in filter '%s'!\n"\
                        "Trying to load with subset of arguments.")  %\
                        self.f.get_name()
                nargs = len(self.r.labels)
                rule = self.r(self.a[0:nargs])
                self.f.add_rule(rule)
            else:
                if len(self.r.labels) > len(self.a):
                    print _("WARNING: Too few arguments in filter '%s'!\n" \
                            "         Trying to load anyway in the hope this "\
                            "will be upgraded.") %\
                            self.f.get_name()
                try:
                    rule = self.r(self.a)
                except AssertionError, msg:
                    print msg
                    print _("ERROR: filter %s could not be correctly loaded. "
                            "Edit the filter!") % self.f.get_name()
                    return
                
                self.f.add_rule(rule)
            
    def characters(self, data):
        pass

    def __upgrade(self):
        """
        Upgrade argument lists to latest version.
        """
        # HasPlace rule has extra locality field in v3.3
        if self.r == Rules.Place.HasPlace and len(self.a) == 8:
            self.a = self.a[0:2] + [u''] + self.a[4:8] + [self.a[3]] + \
                     [self.a[2]]
        # HasNameOf rule has new fields for surnames in v3.3
        if self.r == Rules.Person.HasNameOf and len(self.a) == 7:
            self.a = self.a[0:2] + [self.a[3]] + [self.a[2]] + [self.a[6]] + \
                     [u''] + [self.a[4]] + [u'', u''] + [self.a[5]] + \
                     [u'', u'0']

#-------------------------------------------------------------------------
#
# Name to class mappings
#
#-------------------------------------------------------------------------
# This dict is mapping from old names to new names, so that the existing
# custom_filters.xml will continue working
old_names_2_class = {
    "Everyone"                      : rules.person.Everyone,
    "Is default person"             : rules.person.IsDefaultPerson,
    "Is bookmarked person"          : rules.person.IsBookmarked,
    "Has the Id"                    : rules.person.HasIdOf,
    "Has a name"                    : rules.person.HasNameOf,
    "Has the relationships"         : rules.person.HasRelationship,
    "Has the death"                 : rules.person.HasDeath,
    "Has the birth"                 : rules.person.HasBirth,
    "Is a descendant of"            : rules.person.IsDescendantOf,
    "Is a descendant family member of" : rules.person.IsDescendantFamilyOf,
    "Is a descendant of filter match": rules.person.IsDescendantOfFilterMatch,
    "Is a descendant of person not more than N generations away":
        rules.person.IsLessThanNthGenerationDescendantOf,
    "Is a descendant of person at least N generations away":
        rules.person.IsMoreThanNthGenerationDescendantOf,
    "Is an descendant of person at least N generations away" :
        rules.person.IsMoreThanNthGenerationDescendantOf,
    "Is a child of filter match"    : rules.person.IsChildOfFilterMatch,
    "Is an ancestor of"             : rules.person.IsAncestorOf,
    "Is an ancestor of filter match": rules.person.IsAncestorOfFilterMatch,
    "Is an ancestor of person not more than N generations away" : 
        rules.person.IsLessThanNthGenerationAncestorOf,
    "Is an ancestor of person at least N generations away":
        rules.person.IsMoreThanNthGenerationAncestorOf,
    "Is a parent of filter match"   : rules.person.IsParentOfFilterMatch,
    "Has a common ancestor with"    : rules.person.HasCommonAncestorWith,
    "Has a common ancestor with filter match" :
        rules.person.HasCommonAncestorWithFilterMatch,
    "Is a female"                   : rules.person.IsFemale,
    "Is a male"                     : rules.person.IsMale,
    "Has the personal event"        : rules.person.HasEvent,
    "Has the family event"          : rules.person.HasFamilyEvent,
    "Has the personal attribute"    : rules.person.HasAttribute,
    "Has the family attribute"      : rules.person.HasFamilyAttribute,
    "Has source of"                 : rules.person.HasSourceOf,
    "Matches the filter named"      : rules.person.HasSourceOf,
    "Is spouse of filter match"     : rules.person.IsSpouseOfFilterMatch,
    "Is a sibling of filter match"  : rules.person.IsSiblingOfFilterMatch,
    "Relationship path between two people" :
        rules.person.RelationshipPathBetween,
    "Relationship paths between a person and a list of people" :
        rules.person.DeepRelationshipPathBetween,
    "People who were adopted"       : rules.person.HaveAltFamilies,
    "People who have images"        : rules.person.HavePhotos,
    "People with children"          : rules.person.HaveChildren,
    "People with incomplete names"  : rules.person.IncompleteNames,
    "People with no marriage records" : rules.person.NeverMarried,
    "People with multiple marriage records": rules.person.MultipleMarriages,
    "People without a birth date"   : rules.person.NoBirthdate,
    "People with incomplete events" : rules.person.PersonWithIncompleteEvent,
    "Families with incomplete events" :rules.person.FamilyWithIncompleteEvent,
    "People probably alive"         : rules.person.ProbablyAlive,
    "People marked private"         : rules.person.PeoplePrivate,
    "People marked public"         : rules.person.PeoplePublic,
    "Witnesses"                     : rules.person.IsWitness,
    "Has text matching substring of": rules.person.HasTextMatchingSubstringOf,
}
