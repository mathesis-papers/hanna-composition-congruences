import json
from pathlib import Path


MAX_DEGREE = 96


def multiply(left, right, degree):
    product = [0] * (degree + 1)
    for left_degree, left_value in enumerate(left[:degree + 1]):
        if not left_value:
            continue
        for right_degree, right_value in enumerate(right[:degree - left_degree + 1]):
            if right_value:
                product[left_degree + right_degree] += left_value * right_value
    return product


def compose(outer, inner, degree):
    result = [0] * (degree + 1)
    power = [1] + [0] * degree
    inner_order = next((index for index, value in enumerate(inner) if value), degree + 1)
    assert inner_order > 0
    for exponent, coefficient in enumerate(outer):
        if exponent * inner_order > degree:
            break
        if coefficient:
            for index, value in enumerate(power):
                result[index] += coefficient * value
        power = multiply(power, inner, degree)
    return result


def residual(series, family, degree):
    square = multiply(series, series, degree)
    if family == 'A389474':
        inner = [2 * value for value in square]
        inner[2] += 1
        inner[3] += 2
        composition = compose(series, inner, degree)
        return [value - 3 * square[index] for index, value in enumerate(composition)]
    assert family == 'A389475'
    inner = [0] * (degree + 1)
    inner[2] = 3
    composition = compose(series, inner, degree)
    cube = multiply(square, series, degree)
    result = [value - square[index] + 2 * cube[index]
              for index, value in enumerate(composition)]
    result[2] -= 2
    return result


def construct(family):
    series = [0, 1] + [0] * (MAX_DEGREE - 1)
    for index in range(2, MAX_DEGREE + 1):
        numerator = residual(series, family, index + 1)[index + 1]
        assert numerator % 2 == 0, (family, index, 'parity')
        series[index] = numerator // 2
        assert residual(series, family, index + 1)[index + 1] == 0
    assert not any(residual(series, family, MAX_DEGREE + 1))
    return series


def shifted(series, exponent, degree):
    return [series[index // exponent] if index % exponent == 0 else 0
            for index in range(degree + 1)]


def compare_table(series, family):
    path = Path(__file__).with_name(f'{family}-first96.tsv')
    records = [tuple(map(int, line.split())) for line in path.read_text().splitlines()
               if line and not line.startswith('#')]
    assert [index for index, _ in records] == list(range(1, MAX_DEGREE + 1))
    assert all(series[index] == value for index, value in records)


def inverse(series, degree):
    result = [0, 1] + [0] * (degree - 1)
    for index in range(2, degree + 1):
        result[index] = -compose(series, result, index)[index]
    expected = [0, 1] + [0] * (degree - 1)
    assert compose(series, result, degree) == expected
    assert compose(result, series, degree) == expected
    return result


def power(series, exponent, degree):
    result = [1] + [0] * degree
    if exponent > degree and not series[0]:
        return [0] * (degree + 1)
    for _ in range(exponent):
        result = multiply(result, series, degree)
    return result


def general_residual(series, family, parameter, degree):
    square = multiply(series, series, degree)
    inner = [0] * (degree + 1)
    if family == 'odd-A':
        odd = 2 * parameter + 1
        inner = [2 * parameter * value for value in square]
        inner[2] += 1
        inner[3] += 2 * parameter
        return [value - odd * square[index]
                for index, value in enumerate(compose(series, inner, degree))]
    if family in {'odd-B', 'signed'}:
        inner[2] = parameter
        factor = parameter if family == 'signed' else 1
        result = [factor * value - square[index] + 2 * cube
                  for index, (value, cube) in enumerate(zip(
                      compose(series, inner, degree), multiply(square, series, degree)))]
        if family == 'odd-B':
            result[2] -= parameter - 1
        return result
    assert family == 'prime'
    inner[parameter] = 1
    prime_power = power(series, parameter, degree)
    next_power = multiply(prime_power, series, degree)
    return [value - prime_power[index] + parameter * next_power[index]
            for index, value in enumerate(compose(series, inner, degree))]


def general_construct(family, parameter, degree):
    denominator = parameter if family == 'prime' else 2
    shift = parameter - 1 if family == 'prime' else 1
    series = [0, 1] + [0] * (degree - 1)
    for index in range(2, degree + 1):
        numerator = general_residual(series, family, parameter, index + shift)[index + shift]
        assert numerator % denominator == 0, (family, parameter, index, 'divisibility')
        series[index] = numerator // denominator
    assert not any(general_residual(series, family, parameter, degree + shift))
    return series


def linked_table(series, name):
    records = [tuple(map(int, line.split()))
               for line in Path(__file__).with_name(name + '-first30.tsv').read_text().splitlines()
               if line and not line.startswith('#')]
    assert [index for index, _ in records] == list(range(1, 31))
    assert all(series[index] == value for index, value in records)


def extension_checks(first, second):
    degree = 30
    odd_parameters = list(range(-5, 8, 2))
    for odd in odd_parameters:
        parameter = (odd - 1) // 2
        series = general_construct('odd-A', parameter, degree)
        square = multiply(series, series, degree)
        assert square[4] == parameter * odd ** 2
        assert all((value - {2: 1, 3: 2 * parameter}.get(index, 0)) % (odd ** 2) == 0
                   for index, value in enumerate(square))
        companion = general_construct('odd-B', odd, degree)
        if odd == 3:
            assert series == first[:degree + 1]
            assert companion == second[:degree + 1]
        for prime in [3, 5, 7]:
            if odd % prime == 0:
                cube = multiply(multiply(companion, companion, degree), companion, degree)
                companion_square = multiply(companion, companion, degree)
                assert all((value - (1 if index == 2 else 0) - 2 * cube[index]) % prime == 0
                           for index, value in enumerate(companion_square))
    prime_series = {}
    for prime in [2, 3, 5, 7]:
        series = general_construct('prime', prime, degree)
        prime_series[prime] = series
        reverse = inverse(series, degree)
        polynomial = [0] * (degree + 1)
        polynomial[prime] = 1
        polynomial[prime + 1] = -prime
        assert compose(reverse, polynomial, degree) == power(reverse, prime, degree)
        iterate = [0, 1] + [0] * (degree - 1)
        for iterations in range(4):
            assert compose(series, power(reverse, prime ** iterations, degree), degree) == iterate
            iterate = compose(polynomial, iterate, degree)
    linked_table(prime_series[2], 'A273095')
    linked_table(prime_series[3], 'A274396')
    assert prime_series[2] == general_construct('odd-B', 1, degree)
    for sign in [-1, 1]:
        series = general_construct('signed', sign, degree)
        reverse = inverse(series, degree)
        inner = [sign * value for value in multiply(reverse, reverse, degree)]
        expected = [0] * (degree + 1)
        expected[2], expected[3] = 1, -2
        assert [sign * value for value in compose(series, inner, degree)] == expected
        assert compose(reverse, [sign * value for value in expected], degree) == inner
        if sign == -1:
            linked_table(series, 'A273320')
    examples = [first, second, prime_series[2], prime_series[3],
                general_construct('signed', -1, degree)]
    coefficient_pairs = 0
    for series in examples:
        for prime in [2, 3, 5, 7]:
            substitution = shifted(series, prime, degree)
            for height in [1, 2, 3]:
                for exponent in range(degree // prime ** height + 1):
                    left = power(series, prime ** height * exponent, degree)
                    right = power(substitution, prime ** (height - 1) * exponent, degree)
                    modulus = prime ** height
                    remaining_exponent = exponent
                    while remaining_exponent and remaining_exponent % prime == 0:
                        modulus *= prime
                        remaining_exponent //= prime
                    assert all((left_value - right_value) % modulus == 0
                               for left_value, right_value in zip(left, right))
                    coefficient_pairs += degree + 1
    control = [0, 1, 1] + [0] * (degree - 2)
    sharpness_cases = 0
    for prime in [2, 3, 5, 7]:
        for height in [1, 2, 3]:
            for exponent in range(1, (degree - 1) // prime ** height + 1):
                total_exponent = prime ** height * exponent
                left = power(control, total_exponent, degree)
                right = power(shifted(control, prime, degree), prime ** (height - 1) * exponent, degree)
                assert left[total_exponent + 1] - right[total_exponent + 1] == total_exponent
                sharpness_cases += 1
    assert general_residual([0, 1, 1], 'prime', 4, 6)[6] == 14
    return {'degree': degree, 'odd_parameters': odd_parameters,
            'prime_family_parameters': [2, 3, 5, 7], 'signed_parameters': [-1, 1],
            'linked_oeis_table_matches': 90, 'iteration_heights': [0, 3],
            'prime_power_heights': [1, 3], 'prime_power_coefficient_pairs': coefficient_pairs,
            'prime_power_modulus': 'p^(r+v_p(k)) for k>0; zero difference for k=0',
            'prime_power_sharpness_cases': sharpness_cases,
            'composite_degree_four_cubic_coefficient': '7/2'}


def main():
    first = construct('A389474')
    second = construct('A389475')
    for family, series in [('A389474', first), ('A389475', second)]:
        compare_table(series, family)
    square_first = multiply(first, first, MAX_DEGREE)
    for index, value in enumerate(square_first):
        expected = {2: 1, 3: 2}.get(index, 0)
        assert (value - expected) % 9 == 0
    assert square_first[4] == 9
    cube_first = multiply(square_first, first, MAX_DEGREE)
    substitution_first = shifted(first, 3, MAX_DEGREE)
    left_power = right_power = [1] + [0] * MAX_DEGREE
    for exponent in range(MAX_DEGREE // 3 + 1):
        assert all((left - right) % 3 == 0
                   for left, right in zip(left_power, right_power))
        left_power = multiply(left_power, cube_first, MAX_DEGREE)
        right_power = multiply(right_power, substitution_first, MAX_DEGREE)
    square_second = multiply(second, second, MAX_DEGREE)
    cube_second = multiply(square_second, second, MAX_DEGREE)
    substitution_second = shifted(second, 3, MAX_DEGREE)
    for index in range(MAX_DEGREE + 1):
        assert (cube_second[index] - substitution_second[index]) % 3 == 0
        assert (square_second[index] - 2 * substitution_second[index]
                - (1 if index == 2 else 0)) % 3 == 0
        if index % 2 and index >= 3:
            assert square_second[index] == 2 * cube_second[index]
        if index % 2 == 0 and index >= 4:
            assert square_second[index] == (3 ** (index // 2) * second[index // 2]
                                             + 2 * cube_second[index])
    inverse_degree = 32
    inverse_first = inverse(first, inverse_degree)
    inverse_second = inverse(second, inverse_degree)
    inner = multiply(inverse_first, inverse_first, inverse_degree)
    cube_inverse = multiply(inner, inverse_first, inverse_degree)
    inner = [value + 2 * cube_inverse[index] + (2 if index == 2 else 0)
             for index, value in enumerate(inner)]
    expected = [3 if index == 2 else 0 for index in range(inverse_degree + 1)]
    assert compose(first, inner, inverse_degree) == expected
    squared_inverse = multiply(inverse_second, inverse_second, inverse_degree)
    inner = [3 * value for value in squared_inverse]
    expected = [2 * value + (1 if index == 2 else 0) - (2 if index == 3 else 0)
                for index, value in enumerate(squared_inverse)]
    assert compose(second, inner, inverse_degree) == expected
    catalan = [0, 1] + [0] * (MAX_DEGREE - 1)
    for index in range(2, MAX_DEGREE + 1):
        catalan[index] = sum(catalan[left] * catalan[index - left]
                             for left in range(1, index))
    square_catalan = multiply(catalan, catalan, MAX_DEGREE)
    inner = [0] * (MAX_DEGREE + 1)
    inner[2] = 1
    for index in range(1, MAX_DEGREE + 1):
        inner[index] += 2 * square_catalan[index - 1]
    assert compose(catalan, inner, MAX_DEGREE) == square_catalan
    output = {
        'arithmetic': 'exact integers',
        'series_coefficients': {'A389474': [1, MAX_DEGREE], 'A389475': [1, MAX_DEGREE]},
        'oeis_table_matches': 2 * MAX_DEGREE,
        'even_triangular_numerators': 2 * (MAX_DEGREE - 1),
        'defining_equations_degrees': [0, MAX_DEGREE + 1],
        'congruence_degrees': [0, MAX_DEGREE],
        'formula_four_k': [0, MAX_DEGREE // 3],
        'formula_four_coefficient_pairs': (MAX_DEGREE // 3 + 1) * (MAX_DEGREE + 1),
        'reversion_identities_degrees': [0, inverse_degree],
        'catalan_comparison_degrees': [0, MAX_DEGREE],
        'extensions': extension_checks(first, second),
        'scope': 'finite coefficient checks; all-degree statements have written proofs in note.tex',
        'status': 'PASS'
    }
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
