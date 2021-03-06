import re
from logging import getLogger
from typing import Sequence

from ..helpers.primer import Gene
from ..helpers import run_and_feed


log = getLogger(__name__)


class Cofolder:
    def __init__(self, config):
        self.config = config

    def get_mfe(self, rnac_output, pos):
        mfes = []
        for i in range(2, 12, 3):
            m = re.search(r"-?\d+[.]\d+", rnac_output[pos + i])
            mfes.append(float(m.group(0)))

        return min(mfes)

    def cofold(self, gene_set: Sequence[Gene], linkers):
        cofold_string_list = []
        pos = 0
        positions = dict()
        # add adapter here!

        for i in range(0, len(gene_set)):
            for j in range(i, len(gene_set)):
                # iterate over amplicons
                for k in range(0, len(gene_set[i].amplicons)):
                    for l in range(0, len(gene_set[j].amplicons)):
                        for pair1 in gene_set[i].amplicons[k].primer_set:
                            for pair2 in gene_set[j].amplicons[l].primer_set:
                                positions[f"{pair1.name}_{k}&{pair2.name}_{l}"] = pos
                                pos += 12
                                cofold_string_list += [
                                    f">{pair1.name}_{k}_fwd&{pair2.name}_{l}_fwd\n",
                                    f"{linkers[0]}{pair1.fwd.sequence}&{linkers[0]}{pair2.fwd.sequence}\n",
                                    f">{pair1.name}_{k}_rev&{pair2.name}_{l}_rev\n",
                                    f"{linkers[1]}{pair1.rev.sequence}&{linkers[1]}{pair2.rev.sequence}\n",
                                    f">{pair1.name}_{k}_fwd&{pair2.name}_{l}_rev\n",
                                    f"{linkers[0]}{pair1.fwd.sequence}&{linkers[1]}{pair2.rev.sequence}\n",
                                    f">{pair1.name}_{k}_rev&{pair2.name}_{l}_fwd\n",
                                    f"{linkers[1]}{pair1.rev.sequence}&{linkers[0]}{pair2.fwd.sequence}\n",
                                ]

        # this is way faster than concatenating the strings inside the loop
        cofold_string = "".join(cofold_string_list)

        log.info("Running cofold prediction...")

        p = run_and_feed(
            self.config.rnacf_path,
            noPS=True,
            noLP=True,
            P="dna_mathews2004.par",
            _input_str=cofold_string,
        )
        rnac_output = p.stdout.strip().split("\n")

        for i in range(0, len(gene_set)):
            mfe_list = []
            for k in range(0, len(gene_set[i].amplicons)):
                mfe_list.append([])
                for pair_index, pair1 in enumerate(gene_set[i].amplicons[k].primer_set):
                    mfe_list[k].append([])
                    for j in range(0, len(gene_set)):
                        mfe_list[k][pair_index].append([])
                        for l in range(0, len(gene_set[j].amplicons)):
                            mfe_list[k][pair_index][j].append([])
                            for pair_index2, pair2 in enumerate(
                                gene_set[j].amplicons[l].primer_set
                            ):
                                if i <= j:
                                    pos = positions[
                                        pair1.name
                                        + "_"
                                        + str(k)
                                        + "&"
                                        + pair2.name
                                        + "_"
                                        + str(l)
                                    ]
                                else:
                                    pos = positions[
                                        pair2.name
                                        + "_"
                                        + str(l)
                                        + "&"
                                        + pair1.name
                                        + "_"
                                        + str(k)
                                    ]

                                mfe = abs(self.get_mfe(rnac_output, pos))
                                mfe_list[k][pair_index][j][l].append(mfe)
            gene_set[i].mfes = mfe_list
