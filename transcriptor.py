
import numpy as np


def bb_intersection_over_union(boxA, boxB):
	# determine the (x, y)-coordinates of the intersection rectangle
	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[2], boxB[2])
	yB = min(boxA[3], boxB[3])
	# compute the area of intersection rectangle
	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
	# compute the area of both the prediction and ground-truth
	# rectangles
	boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
	boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
	# compute the intersection over union by taking the intersection
	# area and dividing it by the sum of prediction + ground-truth
	# areas - the interesection area
	iou = interArea / float(boxAArea + boxBArea - interArea)
	# return the intersection over union value
	return iou

def bounding_box_center(points: list) -> tuple:
    return (int(((points[1][0] - points[0][0])/2)+points[0][0])  , int(((points[1][1] - points[0][1])/2)+points[0][1] ))

def is_inside(bb, p):
   br = bb[1]
   tl = bb[0]
   if (p[0] > tl[0] and p[0] < br[0] and p[1] > tl[1] and p[1] < br[1]) :
      return True
   else :
      return False


class Transcriptor():

    def __call__(self, bbs: np.ndarray) -> str:
        """ bbs must be an array cointaining: list[tuple([(x1,y1), (x2,y2)], label, conf)] """
        
        numbers = self.get_numbers(bbs)
        operation = self.get_operation(bbs)
        y_equals = self.get_equals_position(bbs)
        oversets = self.get_oversets(bbs)
        result_digits, terms_digits = self.divide_result_and_terms(numbers, y_equals)
        result = self.get_result(result_digits, y_equals)
        term1, term2 = self.find_terms(terms_digits)
        new_terms1, remain_oversets = self.link_oversets(oversets, term1)
        new_terms2, _ = self.link_oversets(remain_oversets, term2)
        equation = self.turn_to_latex(new_terms1, new_terms2, operation[1])
        latex = f'{equation} = {result}'
        return latex

    def get_numbers(self, bbs):
        return [item for item in bbs if item[1].isnumeric()]

    def get_oversets(self, bbs):
        return [item for item in bbs if "c1" == item[1]]

    def get_operation(self, bbs):
        try:
            operation = [item for item in bbs if "+" == item[1] or "-" == item[1]][0]
        except:
            return (0, "?")
        return operation

    def get_equals_position(self, bbs):
        equals = [item for item in bbs if "=" == item[1]][0] # Melhorar (Caso detect 2, por ex)
        center = bounding_box_center(equals[0])
        return center[1]

    def divide_result_and_terms(self, numbers, y_equals):
        result, terms = [], []
        for x in numbers:
            (result, terms)[bounding_box_center(x[0])[1] < y_equals].append(x)
        return result, terms

    def get_result(self, bbs, y_equals):
        #filtered = [item for item in numbers if bounding_box_center(item[0])[1] > y_equals]
        bbs = sorted(bbs, key=lambda x: x[0][0][0])
        digits = [item[1] for item in bbs]
        result = ' '.join(digits)
        return result

    def find_terms(self, bbs):
        """Returns only two terms"""
        distances = []
        bbs = sorted(bbs, key=lambda x: x[0][0][1])
        for i, j in enumerate(bbs[:-1]):
            distance = bbs[i+1][0][0][1] - j[0][0][1]
            distances.append(distance)
        
        index = distances.index(max(distances))
        term1 = bbs[:index+1]
        term2 = bbs[index+1:]
        term1 = sorted(term1, key=lambda x: x[0][0][0])
        term2 = sorted(term2, key=lambda x: x[0][0][0])
        return term1, term2

    def link_oversets(self, oversets, terms):
        new_terms = []
        terms = sorted(terms, key=lambda x: x[0][0][0], reverse=True)
        # TODO: LEMBRAR DE ORDENAR OS OVERSETS (DIREITA PARA ESQUERDA)
        ys = []
        for term in terms:
            ys.append(term[0][1][1])
            width = term[0][1][0] - term[0][0][0]
            x_factor = int(width*0.6)
            y_factor = int(width*1.2)

            p1 = (term[0][0][0]-x_factor, term[0][0][1]-y_factor)
            p2 = (term[0][1][0]+x_factor, term[0][1][1]-width)

            linked = False

            for j in range(len(oversets)):
                if oversets[j] == 0:
                    continue

                center_overset = bounding_box_center(oversets[j][0])
                inside = is_inside((p1, p2), center_overset)

                if inside:
                    linked = True
                    new_terms.append((term, oversets[j]))
                    oversets[j] = 0
                    break

            if not linked:
                new_terms.append((term, 0))

        new_terms = sorted(new_terms, key=lambda x: x[0][0][0][0])
        remain_oversets = [elem for elem in oversets if not elem == 0]

        y_terms = min(ys)
        extra_oversets = [overset for overset in remain_oversets if overset[0][1][1] < y_terms]

        this_extra_oversets, other_terms_oversets = [], []
        for overset in remain_oversets:
            (this_extra_oversets, other_terms_oversets)[ overset[0][1][1] > y_terms].append(overset)

        new_terms = this_extra_oversets + new_terms

        return new_terms, other_terms_oversets

    def turn_to_latex(self, terms1, terms2, operation):
        latex1 = []
        latex2 = []
        for term in terms1:
            if term[1] == 'c1':
                latex1.append("\overset { 1 } { }")
            elif term[1] == 0:
                latex1.append(term[0][1])
            else:
                latex1.append("\overset { 1 } { "+term[0][1]+" }")

        for term in terms2:
            if term[1] == 'c1':
                latex2.append("\overset { 1 } { }")
            elif term[1] == 0:
                latex2.append(term[0][1])
            else:
                latex2.append("\overset { 1 } { "+term[0][1]+" }")

        latex1 = ' '.join(latex1)
        latex2 = ' '.join(latex2)
        return f'{latex1} {operation} {latex2}'
