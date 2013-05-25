# Copyright (c) 2010 Martin Abente Lahaye. - martin.abente.lahaye@gmail.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA

from check import get_contents, get_characters

TIBIA_GUILD_URI = '/community/?subtopic=guilds&page=view&GuildName='

GUILD_SPLIT_STR = '\n'
GUILD_STOP_STR = '\">'


def get_guild_characters(name):
    contents = get_contents([TIBIA_GUILD_URI+name])
    characters = get_characters(contents[0], GUILD_SPLIT_STR, GUILD_STOP_STR)
    return characters
