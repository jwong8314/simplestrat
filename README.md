# SimpleStrat

Official implementation of [SimpleStrat: Diversifying Language Model Generation with Stratification (Neurips'25)](https://github.com/jwong8314/simplestrat)

## Overview

Post-training causes significant loss to diversity.
To study this we introduce: 
- Taxonomy of approaches to measure diversity
- CoverageQA: wikidata-based dataset of 155 multi-answer questions to measure diversity. 
- SimpleStrat: autostratification method that shows improved diversity for both proprietary models and open-weight models
    - Up to 5X improvement to recall on CoverageQA
    - Same diversity at temperature 0 as temperature 1 without losing quality on Creative Writing


## Data

The `data/` directory contains coverageQA dataset introduce in SimpleStrat.

## Project Structure

```
simplestrat/
├── data/          # Data files and datasets
└── README.md      # This file
```


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[License information to be added]

## Citation

If you use SimpleStrat for your research or application, please cite our paper:

```
@article{wong2024simplestrat,
  title={Simplestrat: Diversifying language model generation with stratification},
  author={Wong, Justin and Orlovskiy, Yury and Luo, Michael and Seshia, Sanjit A and Gonzalez, Joseph E},
  journal={arXiv preprint arXiv:2410.09038},
  year={2024}
}
```

## Contact

For questions reach out at [wong.justin@berkeley.edu](wong.justin@berkeley.edu), we'd love to chat!

