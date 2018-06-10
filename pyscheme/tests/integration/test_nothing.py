# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from .base import Base


class TestNothing(Base):

    def test_nothing_eq_nothing(self):
        self.assertEval(
            'true',
            '''
            nothing == nothing;
            '''
        )

    def test_nothing_doesnt_print(self):
        self.assertEval(
            '',
            'nothing;'
        )
