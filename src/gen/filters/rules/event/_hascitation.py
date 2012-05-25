#
# Gramps - a GTK+/GNOME based genealogy program
#
# Copyright (C) 2002-2006  Donald N. Allingham
# Copyright (C) 2011       Tim G L Lyons
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

"""
Filter rule to match event with a particular citation.
"""
#-------------------------------------------------------------------------
#
# Standard Python modules
#
#-------------------------------------------------------------------------
from gen.ggettext import gettext as _

#-------------------------------------------------------------------------
#
# GRAMPS modules
#
#-------------------------------------------------------------------------
from gen.filters.rules._hascitationbase import HasCitationBase

#-------------------------------------------------------------------------
#
# HasEvent
#
#-------------------------------------------------------------------------
class HasCitation(HasCitationBase):
    """Rule that checks for an event with a particular value"""

    labels      = [ _('Volume/Page:'), 
                    _('Date:'), 
                    _('Confidence level:')]
    name        =  _('Event with the <citation>')
    description = _("Matches events with a citation of a particular "
                    "value")
    
    def apply(self, dbase, event):
        for citation_handle in event.get_citation_list():
            citation = dbase.get_citation_from_handle(citation_handle)
            if HasCitationBase.apply(self, dbase, citation):
                return True
        return False
