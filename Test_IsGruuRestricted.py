import unittest
import copy

class Gateway(object):
    def __init__(self, isLBRRestricted=False, siteId=""):
        self.IsLBRRestricted = isLBRRestricted
        self.SiteId = siteId

def IsGruuRestricted_Origin(targetList, sourceSite, isFromRestrctedGateway):

    isRestricted = targetList[0].IsLBRRestricted or isFromRestrctedGateway;
    siteid = targetList[0].SiteId;

    for i in range(1, len(targetList)):
        if targetList[i].SiteId.lower() != siteid.lower():
            if not siteid:
                 siteid = targetList[0].SiteId;
            else:
                return True

    if isRestricted:
        if not sourceSite:
            return True

        if sourceSite.lower() == siteid.lower():
            return False

        return True

    return False

def IsGruuRestricted_Ver2(targetList, sourceSite, isFromRestrctedGateway):
    isRestricted = targetList[0].IsLBRRestricted or isFromRestrctedGateway;
    siteid = targetList[0].SiteId;

    for i in range(1, len(targetList)):
        if targetList[i].SiteId.lower() != siteid.lower():
            if not siteid:
                 siteid = targetList[i].SiteId;
            else:
                return True

    if isRestricted:
        if not sourceSite:
            return True

        if sourceSite.lower() == siteid.lower():
            return False

        return True

    return False

def IsGruuRestricted_New(targetList, sourceSite, isFromRestrctedGateway):
    lbrEnabledGatewayFound = targetList[0].IsLBRRestricted
    gatewayFromDiffSiteFound = False
    siteId = targetList[0].SiteId

    for i in range(1, len(targetList)):
        if targetList[i].IsLBRRestricted:
            lbrEnabledGatewayFound = True

        if targetList[i].SiteId.lower() != siteId.lower():
            gatewayFromDiffSiteFound = True

        if lbrEnabledGatewayFound and gatewayFromDiffSiteFound:
            return True

    if not lbrEnabledGatewayFound:
        return False

    if not sourceSite:
        return True

    if sourceSite.lower() == siteId.lower():
        return False

    return True

class TestHelper(object):
    @staticmethod
    def subsets(set1):
        if not set1:
            return set1

        ret = []
        sub_set = []
        for set_size in range(len(set1) + 1):
            TestHelper.subset_helper(set1, ret, sub_set, 0, set_size)
        return ret

    @staticmethod
    def subset_helper(set1, ret, sub_set, index, set_size):
        if len(sub_set) == set_size:
            ret.append(copy.deepcopy(sub_set))
            return

        for i in range(index, len(set1)):
            sub_set.append(set1[i])
            TestHelper.subset_helper(set1, ret, sub_set, i + 1, set_size)
            sub_set.pop()

    @staticmethod
    def generate_repeat(set1):
        if not set1:
            return set1

        ret = []
        result = []

        for size in range(2, len(set1) + 1):
            for item in set1:
                result = []
                while len(result) < size:
                    result.append(item)
                ret.append(copy.deepcopy(result))

        return ret

    @staticmethod
    def permute(set1):
        if not set1:
            return set1

        ret = []
        TestHelper.permutation_helper(set1, ret, 0)
        return ret

    @staticmethod
    def permutation_helper(set1, ret, index):
        if index == len(set1):
            ret.append(copy.deepcopy(set1))
            return

        for i in range(index, len(set1)):
            set1[index], set1[i] = set1[i], set1[index]
            TestHelper.permutation_helper(set1, ret, index + 1)
            set1[index], set1[i] = set1[i], set1[index]

class Test_IsGruuRestricted(unittest.TestCase):
    @staticmethod
    def get_site_combo(site_list):
        set1 = ["", "site1", "site2"]
        subsets = TestHelper.subsets(set1)
        ret = TestHelper.generate_repeat(set1)
        for i in range(len(subsets)):
            ret += TestHelper.permute(subsets[i])

        print("Test Data:" + str(ret))
        return ret

    @staticmethod
    def gen_test_case(method_to_test, expected, targetList, target_sites, source_site, isLBRRestricted, index):
        def test(self):
            actual = method_to_test(targetList, source_site, isLBRRestricted)

            if actual != expected:
                print("Failure:>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print("Expected: " + str(expected) + " Actual: " + str(actual))
                print("Target sites: " + str(target_sites))
                print("Index: " + str(index))
                print("source site:" + source_site)
                print("isLBRRestricted: " + str(isLBRRestricted))
                print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            self.assertTrue(actual == expected)
        return test


    @staticmethod
    def gen_tests(method_to_test, site_config, source_site, expected_result):
        assert method_to_test
        site_combos = Test_IsGruuRestricted.get_site_combo(list(site_config.keys()))
        assert len(site_combos) == len(expected_result)
        i = 0
        for target_sites in site_combos:
            #for source_site, isLBRRestricted in site_config.items():
                targetList = []
                for siteId in target_sites:
                    isLBRRestricted = site_config[siteId]
                    targetList.append(Gateway(siteId=siteId, isLBRRestricted=isLBRRestricted))
                test_method = Test_IsGruuRestricted.gen_test_case(method_to_test, expected_result[i], targetList, target_sites, source_site, isLBRRestricted, i)
                source_site_display_name = source_site or "empty"
                test_name = "test_{}_{}_lbr_{}_{:5d}".format(method_to_test.__name__, source_site_display_name, str(isLBRRestricted), i)
                test_method.__name__ = test_name
                i += 1
                setattr(Test_IsGruuRestricted, test_method.__name__, test_method)

if __name__ == '__main__':
    site_config1 = {
        '': False,
        'site1': False,
        'site2': True,
    }
    exprected_result1 = [False, False, True, False, False, True, False, False, True, False, False, True, True, True, True, True, True, True, True, True, True]
    #Test_IsGruuRestricted.gen_tests(IsGruuRestricted_New, site_config1, '', expected_result=exprected_result1)
    #Test_IsGruuRestricted.gen_tests(IsGruuRestricted_Origin, site_config1, '', expected_result=exprected_result1)
    Test_IsGruuRestricted.gen_tests(IsGruuRestricted_Ver2, site_config1, '', expected_result=exprected_result1)
    unittest.main(verbosity=2)

